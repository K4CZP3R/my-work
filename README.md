# MyWork

[![codecov](https://codecov.io/gh/K4CZP3R/my-work/branch/master/graph/badge.svg?token=CUFP2TU7O6)](https://codecov.io/gh/K4CZP3R/my-work)

This is the backend of my "My Work" web app. I've created it so I can easily manage payments I need to issue for the people I'm helping in IT.

The end application will contain
- [x] Generating PDF invoices (`Simple PDF Invoice can already be obtained`)
- [ ] Making (iDeal) payment requests
- [ ] Sending payment requests / invoices via email.

## Testing 

Every commit is tested and the coverage is calculated. To test it live you can use the postman collection/environment.

## Running it

First venv, then pip and finally `uvicorn main:app --reload --port 8080`
