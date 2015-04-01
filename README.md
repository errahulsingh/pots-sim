# Heroku Creation

Uses [custom buildpack](https://github.com/thenovices/heroku-buildpack-scipy) to
get SciPy working (requires 2.7.9 runtime):

    heroku create --buildpack https://github.com/thenovices/heroku-buildpack-scipy -s cedar
