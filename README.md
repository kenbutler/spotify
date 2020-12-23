# Purpose

This project was motivated by my wife wanting to access my curated iTunes playlists on her Spotify account. 
Of course, I am "old school" and refuse to subscribe to any streaming services.
As of February 2018, [Spotify decided to remove the iTunes import feature](https://community.spotify.com/t5/Desktop-Windows/iTunes-import-missing/td-p/4466633).
In other words, taking the _easy_ way out was no longer an option.

Alas, I am a software developer myself and refuse to be shutdown from this inconvenience.

# Requirements
Python 3.7+

(See _requirements.txt_ for confirmation)

| Package | Version |
|:---:|:---:|
| certifi | 2020.4.5.1 |
| chardet | 3.0.4 |
| future | 0.18.2 |
| idna | 2.9 |
| joblib | 0.14.1 |
| numpy | 1.18.4 |
| pandas | 0.24.2 |
| Pillow | 7.1.2 |
| python-dateutil | 2.8.1 |
| pytz | 2020.1 |
| requests | 2.23.0 |
| scikit-learn | 0.22.2.post1 |
| scipy | 1.4.1 |
| six | 1.15.0 |
| urllib3 | 1.25.9 |

# How to Use
To use this project, follow these steps:
1. **Clone down this repository.** Let's call the location of this repository _{ROOT}_
2. **Export iTunes library to {ROOT}/res/.** Typically this involves opening iTunes and selecting _File > Library > Export Library..._
Apple should default to the name of _Library.xml_, but other names are fine too.
Make sure you export this to the resources directory of the repository.
3. **Create a Spotify credentials file.**
The Spotify credentials file should follow this format:
```
<username>
<client id>
<client secret>
[comma-separated list of playlists names to ignore]
```

This transfer utility does _NOT_ assume that any playlists should be ignored. 
There are some playlists that probably should be ignored though. For example:
```
All,Music,Movies,TV Shows,Podcasts,Audiobooks,Library,Purchased,Recently Added,Recently Played,Top 25 Most Played
```
4. **Run _transfer.py_.**
**_CAUTION_**: This should clear all playlists on your Spotify account and make it completely automated through this script.