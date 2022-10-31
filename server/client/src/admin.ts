import $ from "jquery";

(() => {
    function main() {
        $("#compress_btn").click(() => {
            console.log("FIELD:", $("#url_field").val())
            $.post("/", {
                    request_type: "compress",
                    url_data: $("#url_field").val()
                },
                (data:string, status:string) => {
                    console.log("Data: " + data + "\nStatus: " + status);
                    if (status != "success") return
                    $("#short_url_label").text(data)
                });
            window.location.reload();
        });

        $("#logout_btn").click(() => {
            window.location.href = '/login';
        });
        
        $.post("/", {
            request_type: "url_requests",
        },
            (data_str: string, status: string) => {
                console.log("sever request:", data_str, status)
                if (status != "success") return
                const data = JSON.parse(data_str)
                handleData(data);
            }
        )
        
    }

    function handleData(data: JSON[]) {
        const tbodyRef = document.getElementById("urlRequestsBody") as HTMLTableElement;
        const columnNames = Object.keys(data[0]);
        columnNames.shift();

        // console.log(columnNames)

        if (tbodyRef === null) {
            return;
        }
        for (let i = 0; i < data.length; i++) {
            const row = tbodyRef.insertRow(-1);
            columnNames.forEach(function(columnName) {
                const cell = row.insertCell(-1);
                const dataObj = data[i];
                const dataCont = dataObj[columnName as keyof typeof dataObj] as string;
                const dataID = dataObj['url_id' as keyof typeof dataObj] as string;
                if (columnName === "status") {
                    const select = addSelect(dataID);
                    select.value = dataCont;
                    select.addEventListener(
                        'change',
                        function() {statusChange(select.id);},
                        false
                    )
                    cell.appendChild(select);
                    return;
                }
                cell.appendChild(document.createTextNode(dataCont));
            })
            
        }
    }

    function addSelect(id: string) {
        const select = document.createElement("select");
        const attrID = "urlStatus" + id
        select.setAttribute("id", attrID);
        // select.setAttribute("onChange", "statusChange(attrID);");
        
        let option = document.createElement("option");
        option.setAttribute("value", "new");
        option.innerHTML = "new";
        select.appendChild(option);
    
        option = document.createElement("option");
        option.setAttribute("value", "pending");
        option.innerHTML = "pending";
        select.appendChild(option);

        option = document.createElement("option");
        option.setAttribute("value", "accepted");
        option.innerHTML = "accepted";
        select.appendChild(option);

        option = document.createElement("option");
        option.setAttribute("value", "rejected");
        option.innerHTML = "rejected";
        select.appendChild(option);
        
        return select;
    }

    function statusChange(id: string) {
        const control = document.getElementById(id) as HTMLSelectElement;
        const idNum = parseInt(id.split("urlStatus")[1]);
        const newStatus = control.value;
        console.log(idNum + " " + newStatus);
        $.post("/", {
            request_type: "update_status",
            url_id: idNum,
            status: newStatus
        },
            (data_str: string, status: string) => {
                console.log("sever feedback:", data_str, status)
            }
        )
    }
    
    main();
})();
