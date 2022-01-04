

python -m foreverbull service create --name backtest_service --image lhjnilsson/zipline-foreverbull:latest --type backtest

python -m foreverbull backtest create --service-id 44a3e980-1af8-4db4-9904-629150ddc301 --name backtest --config sample_config.json

