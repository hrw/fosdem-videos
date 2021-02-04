# FOSDEM videos

This project generates HTML table of all FOSDEM talks. With links to slides and
videos where possible.

# How to start

First you need to fetch XML file: https://fosdem.org/YEAR/schedule/xml
(substitute YEAR with value). Supported years are 2015 - 2021 (there were no
videos earlier).

Script does not fetch XML on it's own as I have scripts which fetch XML every
half hour and regenerate page if there are any changes.
