# number of concurrent request threads of each target lesson
# avoid too large CONCURRENT_REQUEST, or it will hit the server too hard
# OUGHT TO be int and 1 <= CONCURRENT_REQUEST <= 10
CONCURRENT_REQUEST = 1

# after TIMEOUT, course_selector will drop current request and try again
# OUGHT TO be int and 2 <= TIMEOUT <= 60
TIMEOUT = 5

# time interval between 2 successful request
# avoid too small DELAY, or it will hit the server too hard
# OUGHT TO be int and 1 <= DELAY <= 60
DELAY = 5

# if you use ocproxy and openconnect to VPN to SYSU's intranet,
# set USE_SOCKS5_PROXY = True and SOCKS5_PROXY_PORT to the port you set in ocproxy;
# otherwise(like using openconnect without ocproxy), set USE_SOCKS5_PROXY = False and ommit SOCKS5_PROXY_PORT
USE_SOCKS5_PROXY = False
SOCKS5_PROXY_PORT = 1080