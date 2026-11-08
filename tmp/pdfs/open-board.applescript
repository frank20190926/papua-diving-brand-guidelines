tell application "Google Chrome"
 activate
 set reviewWindow to make new window
 set bounds of reviewWindow to {0, 33, 1100, 940}
 set URL of active tab of reviewWindow to "file:///Users/frank/Work/13_money/02_%E5%BC%80%E5%8F%91/papua-diving-guidelines/board1-codex.html"
 return id of reviewWindow
end tell
