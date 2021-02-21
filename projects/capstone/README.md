# Udacity Capstone

## Motivation for project
I completed this project as the final project and capstone of Udacity's Nanodegrees program. I am thankful for all the help and guidance Udacity has given me. I am excited for what's to come and for the carreer change I am now posied to make.

## Dependencies
All of this project's dependencies are listed in the requirements.txt file. They can be installed by running: 
``` python
bash pip install -r requirements.txt 
```

## Heroku URL
_____________


## Testing
To run unittests for this application run:

``` python
python test_app.py
```

## API Reference
### Error Handling
Errors are returned as JSON objects in the following format:
``` python
{
  'success': False,
  'message': 400
}
```
The API will return four error types when requests fail:
<ol>
  <li>400: bad request</li>
  <li>401: not found</li>
  <li>403: forbidden request</li>
  <li>404: resource not found</li>
  <li>422: unprocessable</li>
  <li>500: something went wrong</li>
 </ol>
