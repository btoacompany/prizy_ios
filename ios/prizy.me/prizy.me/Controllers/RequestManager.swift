//
//  RequestManager.swift
//  prizy.me
//
//  Created by Jay Rinaldi Fatalla on 2016/10/11.
//  Copyright © 2016 Jay Rinaldi Fatalla. All rights reserved.
//

import Foundation

enum LoginStatus{
    case connectionError
    case failed
    case ok(String)
}

enum RecoverPasswordStatus {
    case connectionError
    case ok
}

typealias LoginHandler = (LoginStatus)->()
typealias RecoverPasswordHandler = (RecoverPasswordStatus)->()
typealias Parameters = Dictionary<String,String>
class RequestManager {
    static let sharedInstance = RequestManager()
    class RedirectManager : NSObject, URLSessionTaskDelegate {
        
        public func urlSession(_ session: URLSession, task: URLSessionTask, willPerformHTTPRedirection response: HTTPURLResponse, newRequest request: URLRequest, completionHandler: @escaping (URLRequest?) -> Swift.Void){
            if response.url == RequestManager.loginURL {
                completionHandler(nil)
                return
            }
            completionHandler(request)
        }
        
    }
    
    
    private static var loginURL = URL(string: "https://www.prizy.me/login/complete")!
    private static var recoverPasswordURL = URL(string: "https://www.prizy.me/forgot_password/submit")!
    private static var registerPushNotURL = URL(string: "https://www.prizy.me/device/ios/register")!
    private static var unregisterPushNotURL = URL(string: "https://www.prizy.me/device/ios/unregister")!
    private var session:URLSession = URLSession(configuration: .ephemeral,
                                                delegate: RedirectManager(),
                                                delegateQueue: OperationQueue.current)
    private var token:String?
    
    func splitCookie(_ cookie:String, forKey key:String) -> String? {
        let components = cookie.replacingOccurrences(of: ";", with: ",").components(separatedBy: ",").map({
            value in
            value.trimmingCharacters(in: .whitespaces)
        })
        
        let result = components.first(where: {
            (value:String) in
            return value .hasPrefix(key)
        })
        return result
    }

    
    func createPostRequest(url:URL,parameters:Parameters) -> URLRequest{
        
        func postBody(_ dictBody: Parameters) ->  Data {
            var body = String()
            var values = Array<String>()
            for (key,value) in dictBody {
                values.append(String .localizedStringWithFormat("%@=%@", key,value))
            }
            body = values.joined(separator: "&")
            return body.data(using: .utf8)!
        }
        
        var request = URLRequest(url: url)
        
        request.httpMethod = "POST"
        request.addValue("application/x-www-form-urlencoded", forHTTPHeaderField: "content-type")
        
        request.httpBody = postBody(parameters)
        return request
    }


    func createPostRequest(url:URL,parameters:Parameters, headers:Parameters) -> URLRequest{
        var request = URLRequest(url: url)
        
        request.httpMethod = "POST"
        
        request.addValue("application/x-www-form-urlencoded", forHTTPHeaderField: "content-type")
        for (keyheader,valueHeader) in headers{
            request.addValue(valueHeader, forHTTPHeaderField: keyheader)
        }

        func postBody(_ dictBody: Parameters) ->  Data {
            var body = String()
            var values = Array<String>()
            for (key,value) in dictBody {
                values.append(String .localizedStringWithFormat("%@=%@", key,value))
            }
            body = values.joined(separator: "&")
            return body.data(using: .utf8)!
        }
       
        request.httpBody = postBody(parameters)
        return request
    }
    
    func updatePushNotificationToken(_ token: String) {
        self.token = token
        print("token:\(token)")
    }
    
    func registerPushNotification() {
        if self.token != nil  {
            if !(SessionManager.sharedInstance.session?.isEmpty)! {
                let sessionKey = SessionManager.sharedInstance.session!
                let request  = self.createPostRequest(url:RequestManager.registerPushNotURL,
                                                      parameters: ["token":self.token!],
                                                      headers:  ["Cookie":sessionKey])
                print ("URL:\(RequestManager.registerPushNotURL)")
                print ("Session:\(sessionKey)")
                let task = session.dataTask(with: request){ (data: Data?, response: URLResponse?, error: Error?) in
                    
                    if let httpResponse = response as? HTTPURLResponse {
                        print(httpResponse.statusCode)
                        switch (httpResponse.statusCode){
                        case 302:
                            print("fail")
                        default:
                            print("OK")
                        }
                    }
                }

                task.resume()
            }
        }
    }
    func unregisterPushNotification() {
        if self.token != nil  {
            let request  = self.createPostRequest(url:RequestManager.unregisterPushNotURL,
                                                             parameters: ["token":self.token!]
                                                             )
            let task = session.dataTask(with: request) { (data: Data?, response: URLResponse?, error: Error?) in
                
                if let httpResponse = response as? HTTPURLResponse {
                    print(httpResponse.statusCode)
                    switch (httpResponse.statusCode){
                    case 302:
                        print("fail")
                    default:
                        print("OK")
                    }
                }
            }

            task.resume()

        }
    }
    

    func login(email:String, password:String, shouldRemember:Bool, handler:@escaping LoginHandler) {
        
        var remember = "0"
        if shouldRemember {
            remember = "0"
        }
        
        let request  = self.createPostRequest(url:RequestManager.loginURL, parameters: ["email":email,
                                                                                        "password":password,
                                                                                        "remember": remember])
        
    
        let task = session.dataTask(with: request) { (data: Data?, response: URLResponse?, error: Error?) in
            if error != nil {
                handler(.connectionError)
                return
            }
            
            if let httpResponse = response as? HTTPURLResponse {
                
                switch (httpResponse.statusCode){
                case 302:
                    if let cookies = httpResponse.allHeaderFields["Set-Cookie"] as? String {
                        if self.splitCookie(cookies, forKey: "_perks_session") != nil{
                          handler(.ok(cookies))
                        }
                    }
                    handler(.failed)
                default:
                    handler(.failed)
                }
            }
        }
        task.resume()
    }
    
    func recoverPassword(_ email:String, handler:@escaping RecoverPasswordHandler) {
        let request  = self.createPostRequest(url:RequestManager.recoverPasswordURL, parameters: ["email":email])
        let task = session.dataTask(with: request) { (data: Data?, response: URLResponse?, error: Error?) in
            if error != nil {
                handler(.connectionError)
                return
            }
            
            if ((response as? HTTPURLResponse) != nil) {
                handler(.ok)
            }
        }
        task.resume()
    }
}
