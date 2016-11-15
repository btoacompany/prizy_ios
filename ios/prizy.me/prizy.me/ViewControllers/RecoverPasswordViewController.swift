//
//  RecoverPasswordViewController.swift
//  prizy.me
//
//  Created by Jay Rinaldi Fatalla on 2016/10/29.
//  Copyright © 2016 Jay Rinaldi Fatalla. All rights reserved.
//

import UIKit

class RecoveryPasswordVC: UIViewController {
    @IBOutlet weak var emailField: UITextField!
    @IBOutlet weak var recoverPassword: UIButton!
    @IBOutlet weak var cancel: UIButton!
    
    let requestManager = RequestManager()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        let view: UIView = self.view
        let gradient: CAGradientLayer = CAGradientLayer()
        gradient.frame = view.bounds
        let startColor = UIColor.init(red: 1.0, green: 0.470588, blue: 0.0, alpha: 1.0)
        let endColor = UIColor.init(red: 1.0, green: 0.764706, blue: 0.0, alpha: 1.0)
        gradient.colors = [startColor.cgColor, endColor.cgColor]
        gradient.startPoint = CGPoint(x:0, y:0.5)
        gradient.endPoint = CGPoint(x:1, y:0.5)
        view.layer.insertSublayer(gradient, at: 0)
        
        self.emailField.attributedPlaceholder = NSAttributedString(string: Localized(.WRD_EMAIL), attributes: [NSForegroundColorAttributeName: UIColor.white.cgColor])
        
        self.recoverPassword.setTitle(Localized(.WRD_RECOVER_PASSWORD), for: .normal)
        
        let text = Localized(.WRD_CANCEL)
        let forgotText = NSMutableAttributedString(string: text)
        let r = NSRange.init(location: 0, length: 6)
        forgotText.addAttribute(NSLinkAttributeName, value: text, range: r)
        self.cancel.setAttributedTitle(forgotText, for: .normal)
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
