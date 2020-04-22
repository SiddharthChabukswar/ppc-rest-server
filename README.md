# ppc-rest-server

## Django-restframework server for ppc.

### Follow the steps to setup the server locally

```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
The server can be found on address : https://localhost:8000/

### Follow the steps to send request from client

Postman a POST request on the url : https://localhost:8000/privacy/
The body of the request must contain:
```
{
"weblink" : "url of the page to be scraped"
}
```
don't forget to set the body to raw:JSON.
