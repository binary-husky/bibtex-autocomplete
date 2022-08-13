# Change Log

## Version 1.1.2 - 2022-06-11

- Add common authors check when matching entries: if your entries has some
  author field then entries will no common authors will be ignored and entries
  with common authors will be boosted
- Add sanity check for found URLs and DOIs, `btac` now queries them and follows
  a few redirections to check they resolve to an existing page
- Some prettier messages and resolve hints for connection errors
- Add `-S/--ignore-ssl` flag
- Add some logic to dispatch crossref's `container-title` and unpaywall's
  `journal-title` between `journal` and `booktitle` fields.

## Version 1.1.1 - 2022-05-27

- Fix decoding error when opening utf-8 files on Windows
- Add extra fields `query-url`, `query-response-time` and `query-status` to data
  dumps file
- Added github actions

## Version 1.1.0 - 2022-05-21

- Now also queries arxiv
- Normalize title before querying, should improve matches for title with special
  characters
- Added `--dump-data` option

## Version 1.0.5 - 2022-04-13

- Fixed a bug which prevented installation on python 3.8
- Dropped python 3.7 support (It didn't work anyway...)

## Version 1.0.4 - 2022-03-31

- Fixed failed output write in inplace mode
- Fixed double warning for extra output in inplace mode
- Fix default output names ignoring parent directory

## Version 1.0.3 - 2022-03-30

- Clarify new field source priorities
- Fixed unpaywall setting unknown months to 1
- Switch to strict mypy type checking
- Unsupport python 3.6 as alive-progress dropped it
- Switch back to custom logger

## Version 1.0.2 - 2022-03-21

- Fixed missing submodules in upload
- Removed color from progress bar to avoid issues
- Fixed color not being reset on some terminals
- Added wheel for real this time
- Switch to root logger to avoid custom dependency (temporary, until
  alive-progress is fixed)
- Rewrote README with more detail on options

## Version 1.0.1 - 2022-03-19

- Add direct url to svg so that it can show up on PyPi

## Version 1.0.0 - 2022-03-19

- Multi-threading requests (one thread per website) vastly improves performance
- Overhauled display log: now with colors and pretty sections
- Added query rate limiter to respect politeness requests
- Print summary of changes in verbose mode
- Stopped writing to stdout -> writes to my_file.btac.bib by default now
- ~~Added wheel distribution~~ upload failed
- Fixed a bug when setting fields with no data
- Fixed a bug with ignored command line arguments

## Version 0.4.0 - 2022-03-16

- Initial version of the script
