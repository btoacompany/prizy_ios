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
        self.emailField.attributedPlaceholder = NSAttributedString(string: Localized(.WRD_EMAIL), attributes: [NSForegroundColorAttributeName: UIColor.white])
        
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
                    let alert  = UIAlertController(title: Localized(.WRD_RECOVER_PASSWORD_ALERT_HEADER), message: Localized(.WRD_RECOVER_PASSWORD_ALERT_MSG), preferredStyle: .alert)
                    let defaultAction = UIAlertAction(title: Localized(.WRD_ALERT_BUTTON_OK), style: .default) {
                      action in
                        self.dismiss(animated: true, completion: nil)
                    }
                    
                    alert.addAction(defaultAction)
                    self.present(alert, animated: true, completion: nil)
                default:
                    let alert  = UIAlertController(title: Localized(.WRD_ERROR_HEADER), message: Localized(.WRD_CONNECTION_ERROR) , preferredStyle: .alert)
                    let defaultAction = UIAlertAction(title: Localized(.WRD_ALERT_BUTTON_OK), style: .default, handler: nil)
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
