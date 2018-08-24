# gmusiccache
Library/Tool which allows tou to cache your gmusic library locally

# WARNING: Use this application on your risk! Gmusiccache developer(s) have no liability for your missing data or blocked accounts.
### If you want to complain about something – please consult the [LICENSE](./LICENSE)

### Requirements
- Python >= 3.6
- active gmusic subscription

### How to
- Install python 3.6 or higher
- Execute command `pip installl -e .` in gmusiccache source directory
  to install the library/tool (note: on linux, sudo may be required for installation)
- Use it:
  `python -m gmusiccache.downloader --login <login> --password <password> --device <gsf device id> --locale <icu locale> --path <path where to store songs>`

### Notes/Troubleshooting
- Please note that python 3.x binary should be in PATH, not python 2.x
- GSF can be obtained using application like [this](https://play.google.com/store/apps/details?id=com.evozi.deviceid)
- If you using two-factor authorization then generate app password and use it when specifying password argument
- On Windows, if you get error, which tells something like "libmagic library is missing" try the following command to fix the issue:
  `pip install python-magic-bin==0.4.14`
  