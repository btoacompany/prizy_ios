//
//  RecoverPasswordViewController.swift
//  prizy.me
//
//  Created by Jay Rinaldi Fatalla on 2016/10/29.
//  Copyright © 2016 Jay Rinaldi Fatalla. All rights reserved.
//

import UIKit

class RecoveryPasswordVC: PrizyVC {
    @IBOutlet weak var emailField: UITextField!
    @IBOutlet weak var recoverPassword: UIButton!
    @IBOutlet weak var cancel: UIButton!
    
    let requestManager = RequestManager()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        self.emailField.attributedPlaceholder = NSAttributedString(string: Localized(.WRD_EMAIL), attributes: [NSForegroundColorAttributeName: UIColor.white.cgColor])
        
        self.recoverPassword.setTitle(Localized(.WRD_RECOVER_PASSWORD), for: .normal)
        
        self.cancel.setUnderlinedTitle(Localized(.WRD_CANCEL), for: .normal)
    }
    
    @IBAction func sendRecoverPassword(_ sender: AnyObject) {
        self.view.endEditing(true)
        if (self.emailField.text != nil) {
            self.requestManager.recoverPassword(self.emailField.text!) {
                status in
                switch status {
                case .ok:
                    let alert  = UIAlertController(title: "Nice", message: "Sent", preferredStyle: .alert)
                    let defaultAction = UIAlertAction(title: "OK", style: .default) {
                      action in
                        self.dismiss(animated: true, completion: nil)
                    }
                    
                    alert.addAction(defaultAction)
                    self.present(alert, animated: true, completion: nil)
                default:
                    let alert  = UIAlertController(title: "Error", message: "Connection error", preferredStyle: .alert)
                    let defaultAction = UIAlertAction(title: "OK", style: .default, handler:nil)
                    alert.addAction(defaultAction)
                    self.present(alert, animated: true, completion: nil)
                }
            }
        }
    }
    
    @IBAction func dismissVC(_ sender: AnyObject) {
        self.view.endEditing(true)
        self .dismiss(animated: true, completion: nil)
    }
    
}
