var Utils = function(){
        var httpRequest = function (url, method, params, callback){
            var http = new XMLHttpRequest();
            http.open(method, url, true);
            if(params){
                http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            }

            http.onreadystatechange = function() {//Call a function when the state changes.
                if(http.readyState == 4 && http.status == 200) {
                    callback(http)
                }
            }

            http.send(params);
        }

        return{
            httpRequest:httpRequest
        }
}()