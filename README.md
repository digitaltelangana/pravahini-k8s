# X-Road

TODO:

- [ ] Add Ingresses
- [ ] Change the logback to log to stdout
- [ ] Mount configuration files as ConfigMaps

Description=X-Road Proxy UI REST API
ExecStart=/usr/share/xroad/bin/xroad-proxy-ui-api
Description=X-Road Proxy
ExecStart=/usr/share/xroad/bin/xroad-proxy
Description=X-Road signer
ExecStart=/usr/share/xroad/bin/xroad-signer
Description=X-Road Automatic Token Login
ExecStart=/usr/share/xroad/autologin/xroad-autologin-retry.sh
Description=X-Road Central Server
ExecStart=/usr/share/xroad/bin/xroad-centralserver-admin-service
Description=X-Road initialization
ExecStartPre=/bin/mkdir -p -m0750 /var/run/xroad
ExecStartPre=/bin/chown xroad:xroad /var/run/xroad
ExecStart=/usr/share/xroad/scripts/xroad-base.sh
Description=X-Road confclient
ExecStart=/usr/share/xroad/bin/xroad-confclient
Description=X-Road Messagelog Archiver
ExecStart=/usr/share/xroad/bin/xroad-messagelog-archiver
Description=X-Road opmonitor daemon
ExecStart=/usr/share/xroad/bin/xroad-opmonitor
Description=X-Road Monitor
ExecStart=/usr/share/xroad/bin/xroad-monitor
Description=X-Road Central Server Management Service
ExecStart=/usr/share/xroad/bin/xroad-centralserver-management-service
Description=X-Road Central Server Registration Service
ExecStart=/usr/share/xroad/bin/xroad-centralserver-registration-service

xroad-addon-messagelog
Message log archiving and cleaning of the message logs
/var/log/xroad/messagelog-archiver.log
xroad-confclient	Client process for downloading global configuration
/var/log/xroad/configuration_client.log
xroad-proxy	Message processing	/var/log/xroad/proxy.log
/var/log/xroad/clientproxy_access.log
/var/log/xroad/serverproxy_access.log
xroad-signer	Manager process for key settings	/var/log/xroad/signer.log
xroad-proxy-ui-api	Management UI and REST API	/var/log/xroad/proxy_ui_api.log
/var/log/xroad/proxy_ui_api_access.log
xroad-monitor	Environmental monitoring	/var/log/xroad/monitor.log
xroad-opmonitor	Operational monitoring	/var/log/xroad/op-monitor.log