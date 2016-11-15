//
//  ViewController.swift
//  prizy.me
//
//  Created by Jay Rinaldi Fatalla on 2016/10/09.
//  Copyright © 2016 Jay Rinaldi Fatalla. All rights reserved.
//

import UIKit
class LoginVC: UIViewController, UITextFieldDelegate{
    @IBOutlet weak var emailField: UITextField!
    @IBOutlet weak var passwordField: UITextField!

    @IBOutlet weak var loginButton: UIButton!
    @IBOutlet weak var forgotButton: UIButton!

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
        
        self.emailField.delegate = self
        self.emailField.attributedPlaceholder = NSAttributedString(string: Localized(.WRD_EMAIL), attributes: [NSForegroundColorAttributeName: UIColor.white.cgColor])
        
        self.passwordField.delegate = self
        self.passwordField.attributedPlaceholder = NSAttributedString(string: Localized(.WRD_PASSWORD), attributes: [NSForegroundColorAttributeName: UIColor.white.cgColor])
        
        self.loginButton.setTitle(Localized(.WRD_LOGIN), for: .normal)
        
        let text = Localized(.WRD_FORGOT_PASSWORD)
        let forgotText = NSMutableAttributedString(string: text)
        let r = NSRange.init(location: 0, length: 13)
        forgotText.addAttribute(NSLinkAttributeName, value: text, range: r)
        self.forgotButton.setAttributedTitle(forgotText, for: .normal)
        
        if !(SessionManager.sharedInstance.session?.isEmpty)! {
            DispatchQueue.main.async(execute: {
                self.transitionTo(.SEGUE_LOGIN_TO_WEB)
            })
        }
        
        // Do any additional setup after loading the view, typically from a nib.
    }
    
    func textFieldShouldReturn(_ textField: UITextField) -> Bool {
   
        textField.resignFirstResponder()
        switch(textField){
        case self.emailField:
            self.passwordField.becomeFirstResponder()
        case self.passwordField:
            self.login(self.loginButton)
        default:
            print("Unknown login screen textfield")
        }
        return true
    }

    
    @IBAction func login(_ sender: UIButton) {
        self.view.endEditing(true)
        self.requestManager.login(email: self.emailField.text!, password: self.passwordField.text!, shouldRemember:false) {
            status in
            switch (status){
            case .connectionError:
                let alert  = UIAlertController(title: "Error", message: "Connection error", preferredStyle: .alert)
                let defaultAction = UIAlertAction(title: "OK", style: .default, handler: nil)
                alert.addAction(defaultAction)
                self.present(alert, animated: true, completion: nil)
            case .failed:
                let alert  = UIAlertController(title: "Failed", message: "Incorrect password", preferredStyle: .alert)
                let defaultAction = UIAlertAction(title: "OK", style: .default, handler: nil)
                alert.addAction(defaultAction)
                self.present(alert, animated: true, completion: nil)
            case .ok(let session):
                SessionManager.sharedInstance.session = session
                self.transitionTo(.SEGUE_LOGIN_TO_WEB)
            }
        }
    }
    
    @IBAction func forgot(_ sender: UIButton)
    {
        self.view.endEditing(true)
        transitionTo(.SEGUE_LOGIN_TO_RECOVER)
    }

    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        if segue.identifier == Segue.SEGUE_LOGIN_TO_WEB.rawValue {
            let vc = segue.destination as! WebVC
            let s = SessionManager.sharedInstance.session!
            print(s)
            vc.session = s
        }
    }

}

