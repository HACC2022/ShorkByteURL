// import * as $ from "jquery";

function popup_main() {
    console.log("Hello Popup!");

    const SERVER_DOMAIN = "localhost"
    const SERVER_PORT = 8000

    chrome.tabs.query({
        active: true,
        currentWindow: true
    }, tabs => {

        // since only one tab should be active and in the current window at once
        // the return variable should only have one entry
        const activeTab = tabs[0];
        // const activeTabId = activeTab.id; // or do whatever you need
        // console.log("Active Tab ID:", activeTabId);
        // console.log("Active Tab URL:", activeTab.url)
        if(activeTab.url === undefined){
            console.error("No url was found... exiting");
            return;
        }
    });
}

popup_main();

