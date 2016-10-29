//
//  WebViewController.swift
//  prizy.me
//
//  Created by Jay Rinaldi Fatalla on 2016/10/09.
//  Copyright © 2016 Jay Rinaldi Fatalla. All rights reserved.
//

import UIKit
import WebKit

class WebVC: UIViewController {
    
    public var session:String = ""
    public weak var webview:WKWebView!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        let webView = WKWebView()
        webView.frame = self.view.frame
        self.view.addSubview(webView)
        self.webview = webView
        self.webview.evaluateJavaScript("document.cookie='\(self.session)';domain='prizy.me';") { (data, error) -> Void in
            self.webview.load({
                var urlRequest = URLRequest(url: URL(string: "https://www.prizy.me/user")!)
                urlRequest.addValue(self.session, forHTTPHeaderField: "Cookie")
                return urlRequest
                }())
        }
        
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
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
