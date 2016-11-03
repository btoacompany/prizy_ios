//
//  SessionManager.swift
//  prizy.me
//
//  Created by Jay Rinaldi Fatalla on 2016/11/03.
//  Copyright © 2016 Jay Rinaldi Fatalla. All rights reserved.
//

import Foundation

class SessionManager {
    let keychainWrapper = KeychainWrapper()
    static let sharedInstance = SessionManager()
    
    var session:String? {
        get {
            return self.keychainWrapper.myObject(forKey: "v_Data") as! String?
        }
        set {
            self.keychainWrapper.mySetObject(newValue!, forKey:kSecValueData)
            self.keychainWrapper.writeToKeychain()
        }
    }
}
