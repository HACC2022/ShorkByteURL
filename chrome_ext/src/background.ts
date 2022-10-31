

function set_page_status(tab:chrome.tabs.Tab) {
    console.log("Set page status");
    if(document.getElementById("shork_url_banner")) return;

    const SERVER_DOMAIN = "localhost"
    const SERVER_PORT = 8000
    
    const post_address = `http://${SERVER_DOMAIN}:${SERVER_PORT}`
    $.post(post_address, {
        request_type: "verify",
        url_data: tab.url
    },
        (data_str: string, status: string) => {
            const data = JSON.parse(data_str)
            if (status != "success") return
            const verified = data.verified === true;
            let color = 'red';
            let banner_text = 'This page is not verified by hawaii.gov'
            if (verified === true) {
                color = 'green';
                console.log("Verified - GREEN")
                banner_text = 'Verified by hawaii.gov'
            }

            // add html
            const banner = document.createElement("div");
            banner.id = "shork_url_banner";

            const banner_button = document.createElement("button")
            banner_button.id = "shork_url_banner_button"
            banner_button.innerHTML = "✕";
            banner_button.onclick = function () {
                banner.remove();
            };
            banner.appendChild(banner_button);

            const banner_content = document.createElement("div");
            banner_content.id = "shork_url_banner_content";
            banner_content.innerHTML = banner_text;
            banner.appendChild(banner_content)
            document.body.insertBefore(banner, document.body.firstChild);

            document.head.innerHTML += `\
<style type="text/css" media="screen"> \
    * {\
        margin: 0;\
        padding: 0;\
    }\
    body {\
        height: 100vh;\
        position: relative;\
        display: flex;\
        flex-direction: column;\
    }\
    div#shork_url_banner {\
        position: fixed;\
        top: 0;\
        left: 0;\
        background-color: ${color};\
        width: 100%;\
        display: block;\
        z-index:10000;\
    }\
    \
    div#shork_url_banner_content {\
        width: 100%;\
        margin: 0 auto;\
        padding: 10px;\
        border: 0px solid #000;\
    }\
    button#shork_url_banner_button {\
        position: absolute;\
        right: 8px;\
        border: none;\
        background: none;\
        top: 50%;
        transform: translateY(-50%);
    }\
</style>`;
        });
}

function main() {
    console.log("Hello World - Background.js!");

    chrome.tabs.onUpdated.addListener(function (tabId, changeInfo, tab) {
        if (changeInfo.status == 'complete') {
            console.log("Page Loaded")
            chrome.scripting.executeScript({
                target: {tabId: tabId, allFrames: true},
                files: ['jquery.2.1.3.min.js'],
            }, () => {
                chrome.scripting.executeScript({
                    target: { tabId: tabId },
                    func: set_page_status,
                    args: [tab]
                }).then();
            });

        }
    })
}

main();