# Django App Skeleton

This the skeleton code that usually needs to be created in order to
pull code out of a django project into a redistributable django
app. In my projects I attempt to pull any reusable code out and create
single purpose redestributable apps from them, but creating the code
to install them over pypi and running the tests is a really repeditive
task.

## What you need to do

### Grab a copy of the repo
`git clone https://github.com/adamhaney/django-app-skeleton`

### Rename the directory to your new app name
`mv django-app-skeleton <your-new-app-name>`

### Rename the subdirector to your new app name
`cd <your-new-app-name>`
`mv appname <your-new-app-name>`

### Remove the old git credentials 
`rm -r .git`
`git commit -A "initial commit"`

### Update setup.py
replace everything in angle brackets with your project specific information