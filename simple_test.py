import foreverbull
from threading import Thread
{"config": {"start_date": "2017-01-01", 
"end_date": "2017-05-31", "benchmark": "AAPL", "assets": ["AAPL", "TSLA"], "timezone": "utc"}}
# Create backtest
create_backtest = {"config": {"start_date": "2017-01-01", "end_date": "2017-06-30",
"benchmark": "AAPL", "assets": ["AAPL", "TSLA"], "timezone": "utc"}}
create_backtest = foreverbull.http.backtest.Backtest.create_backtest(create_backtest)


# Add backtest service to backtest"
# 		req := httptest.NewRequest(http.MethodPost, "/services/containers", 
# strings.NewReader(`{"source":"docker","image":"zipline-foreverbull-11"}`))
#
container = {"source": "docker", "image": "zipline-foreverbull-11"}
container = foreverbull.http.service.Service.create_container(container)
 
#sPost := fmt.Sprintf(`{"name":"int-test","description":"very nice algo, much money", "container_id": %d}`, c.ID)
#req = httptest.NewRequest(http.MethodPost, "/services", strings.NewReader(sPost))
service = {"name": "pythho-test", "description": "niiice algo", "container_id": container['id']}
service = foreverbull.http.service.Service.create_service(service)


# 		req = httptest.NewRequest(http.MethodPost, fmt.Sprintf("/backtests/%d/services", b.ID), 
# strings.NewReader(fmt.Sprintf(`{"id": %d}`, *s.ID)))
print(create_backtest)
rps= foreverbull.http.backtest.Backtest.add_backtest_service(create_backtest['id'], {"id": container['id']})


## "Create session"

# req := httptest.NewRequest(http.MethodPost, fmt.Sprintf("/backtests/%d/sessions", b.ID), nil)
session = foreverbull.http.backtest.Backtest.create_session(create_backtest['id'])

socket_conf = foreverbull.models.Configuration(socket_type = "replier")
socket_conf.host = "127.0.0.1"
socket = foreverbull.socket.NanomsgSocket(socket_conf)
si = {"host": "127.0.0.1", "port": socket_conf.port, "listen": True, "online": True}

#		wi := service.Instance{Host: &msw.Address, Port: &msw.Port, Listen: true, Online: true}
#		data, _ := json.Marshal(wi)

#		paylod := fmt.Sprintf(`{"instances": [%s], "services": []}`, data)
#		req := httptest.NewRequest(http.MethodPost, fmt.Sprintf("/backtests/%d/sessions/%d/run", b.ID, sess.ID), strings.NewReader(paylod))
def worker():
    while True:
        message = socket.recv()
        print("MSG: ",message)
        req = foreverbull.models.Request.load(message)
        print(req.task)
        if req.task == 'backtest_completed':
            break
        rsp = foreverbull.models.Response(task = req.task)
        socket.send(rsp.dump())

t1 = Thread(target=worker)
t1.start()

foreverbull.http.backtest.Backtest.run_session(create_backtest['id'], session['id'],{"instances": [si], "services": []})

t1.join()