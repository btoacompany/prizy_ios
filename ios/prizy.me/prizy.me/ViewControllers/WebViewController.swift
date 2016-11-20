//
//  WebViewController.swift
//  prizy.me
//
//  Created by Jay Rinaldi Fatalla on 2016/10/09.
//  Copyright © 2016 Jay Rinaldi Fatalla. All rights reserved.
//

import UIKit
import WebKit

class WebVC: UIViewController, WKNavigationDelegate {
    
    public var session:String = ""
    public weak var webview:WKWebView!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        self.loadWebView()
    }

    func loadWebView() {
        let webView = WKWebView()
        webView.frame = self.view.frame
        
        self.view.addSubview(webView)
        self.webview = webView
        self.webview.navigationDelegate = self

        self.webview.scrollView.bounces = false;
        self.webview.scrollView.pinchGestureRecognizer?.isEnabled = false;
        self.webview.load({
                var urlRequest = URLRequest(url: URL(string: "https://www.prizy.me/user")!)
                urlRequest.addValue(self.session, forHTTPHeaderField: "Cookie")
                return urlRequest
                }())
        
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        
    }
    
    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
        
    }
    
    func webViewWebContentProcessDidTerminate(_ webView: WKWebView) {
        
    }
    
    func webView(_ webView: WKWebView, didStartProvisionalNavigation navigation: WKNavigation!) {
        
    }
    
    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        let url = navigationAction.request.url!
        var request = navigationAction.request
        if url.host == "www.prizy.me" || url.host == "prizy.me" {
            if url.absoluteString.contains("prizy.me/login") {
                decisionHandler(.cancel)
                self.logout()
            }
            else if request.value(forHTTPHeaderField: "Cookie") == nil {
                request.addValue(self.session, forHTTPHeaderField: "Cookie")
                decisionHandler(.cancel)
                webView.load(request)
            }
        }
        
        decisionHandler(.allow)
    }
    
    func webView(_ webView: WKWebView, decidePolicyFor navigationResponse: WKNavigationResponse, decisionHandler: @escaping (WKNavigationResponsePolicy) -> Void) {
        if let httpResponse = navigationResponse.response as? HTTPURLResponse {
            let url = httpResponse.url!
            if url.absoluteString.contains("www.prizy.me/login") {
                decisionHandler(.cancel)
                self.logout()
                
            }
            decisionHandler(.allow)
        }
    }
    
    func logout() {
        SessionManager.sharedInstance.session=""
        let appDelegate = UIApplication.shared.delegate as! AppDelegate
        appDelegate.dismissToLoginScreen()
    }
    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destinationViewController.
        // Pass the selected object to the new view controller.
    }
    */

}
