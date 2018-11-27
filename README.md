# Netlify-cms-oauth-provider-python-appengine

[Netlify-CMS](https://www.netlifycms.org/) is an open source project that you can use without using Netlify. In order to do so, you need a way to authenticate; one of the ways to do this is using GitHub oAuth. If you're going to do that though, you need a server-side component acting as the oAuth client, allowing your admin users to connect to GitHub's servers to authenticate.

This is that system.

Based on the [Generic Python](https://github.com/davidejones/netlify-cms-oauth-provider-python)
version of the same thing, this extensively rewritten application is a lightweight mostly-generic oauth client, specifically written for [Google AppEngine](https://cloud.google.com/appengine/).

## Benefits

* Use Netlify-CMS on several front end projects withg one lightweight backend shared between them. 
* Deploy simply to AppEngine and forget
* Profit from your free lightweight CMS (it's unlikely your usage fo this will take you over the GAE Free Tier)

## How to use this

* Clone the repo locally
* Set up a [GitHub oAuth App](https://developer.github.com/apps/building-oauth-apps/creating-an-oauth-app/)
* Put your new app's key and secret into the `/app.yaml` file (or manage your secrets another way, as long as they end up as environment variables in the deployed codebase)
* Set up a Google Cloud Platform account and enable AppEngine
* Set up the [GCloud SDK](https://cloud.google.com/sdk/) locally
* Run `gcloud app deploy` from the root of the project folder
* Edit your netlify CMS config to have the following `backend`:

```
backend:
  name: github
  repo: <<user/reponame>> # whichever repo your admin system is going to be affecting
  base_url: https://<<appengine-url>>.appspot.com # the URL you got from the deploy command above
 ```
 
 Then simply login to any running version of your codebase (including locally). 
