# POTS Simulator

Run your audio files through a fake telephone line! Operable as a Python
package or script, or [web service][webservice] that takes file uploads or JSON
requests.

![Bode plot of POTS filter][potsbode]

## Heroku Details

Uses [custom buildpack][scipypack] to get SciPy working (requires 2.7.9 runtime):

    heroku create --buildpack https://github.com/thenovices/heroku-buildpack-scipy


[scipypack]: https://github.com/thenovices/heroku-buildpack-scipy
[webservice]: https://alpine-cupcake-2461.herokuapp.com/pots
[potsbode]: https://github.com/nicktimko/pots-sim/raw/master/docs/pots-bodeplot.png
