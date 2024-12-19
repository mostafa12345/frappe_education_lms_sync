## frappe_education_lms_sync

education_lms_sync for frappe desk

## Install app
use the following commands to install this app  
First get it from this repo

```
bench get-app education_lms_sync https://github.com/mostafa12345/frappe_education_lms_sync
```
add to your site
```
bench --site [site name] install-app education_lms_sync
```
start the frappe app
```
bench --site [site name] clear-cache
bench start
```

## Uninstall app
```
bench --site [site name] remove-from-installed-apps education_lms_sync  
bench remove-app modern_desk  
```
