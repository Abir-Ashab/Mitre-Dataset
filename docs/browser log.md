## Track Browser Log Using ActivityWatch
* Logs all websites you visit (URLs + titles)
* Records time spent per site or app
* Tracks active windows and idle time
* Can track mouse clicks & keyboard (optional, configurable)
* Exports logs in plain text / JSON / CSV


### How to Install ActivityWatch

**Step 1: Download and Install the Core App**

1. Go to the official website: [https://activitywatch.net](https://activitywatch.net)
2. Click **Download**, and choose your OS (Windows, Mac, Linux)
3. Extract the downloaded zip file and **run `activitywatch.exe`** (or appropriate app for your OS)
4. It will start a local server at `http://localhost:5600` where you can view your activity.


**Step 2: Install Browser Extension**

1. For **Chrome**: [ActivityWatch Extension - Chrome Web Store](https://chromewebstore.google.com/detail/activitywatch-web-watcher/nglaklhklhcoonedhgnpgddginnjdadi)
2. After installing, **click the extension icon** and allow permissions when prompted. And manually add from browser like this :  

### Output and Export

1. Visit `http://localhost:5600/#/timeline`. You’ll see detailed logs like:
   * Time started
   * Domain (e.g., `youtube.com`)
   * Title of the page
   * Duration

2. Click the **Raw Data Button**.  Then export the highlighted bucket.
4. Then open the bucket file and you will see json formatted data.
5. Use [https://jsonlint.com/] (https://jsonlint.com/) to format the json nicely.

