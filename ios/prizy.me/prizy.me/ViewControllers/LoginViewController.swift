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
    
    @IBOutlet weak var rememberSwitch: UISwitch!
    @IBOutlet weak var loginButton: UIButton!
    @IBOutlet weak var forgotButton: UIButton!
    
    @IBOutlet weak var emailLabel: UILabel!
    @IBOutlet weak var passwordLabel: UILabel!
    @IBOutlet weak var rememberLabel: UILabel!
    
    let requestManager = RequestManager()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        self.emailField.delegate = self;
        self.passwordField.delegate = self;
        
        self.emailLabel.text = Localized(.WRD_EMAIL)
        self.passwordLabel.text = Localized(.WRD_PASSWORD)
        self.loginButton.setTitle(Localized(.WRD_LOGIN), for: .normal)
        self.forgotButton.setTitle(Localized(.WRD_FORGOT_PASSWORD), for: .normal)
        self.rememberLabel.text = Localized(.WRD_REMEMBER_ME)
        
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
        self.requestManager.login(email: self.emailField.text!, password: self.passwordField.text!, shouldRemember: self.rememberSwitch.isOn) {
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
            case .ok(let sesson):
                let alert  = UIAlertController(title: "Nice", message: sesson, preferredStyle: .alert)
                let defaultAction = UIAlertAction(title: "OK", style: .default, handler: nil)
                alert.addAction(defaultAction)
                self.present(alert, animated: true, completion: nil)
            }
        }
    }
    
    @IBAction func forgot(_ sender: UIButton)
    {
        self.view.endEditing(true)
        transitionTo(.SEGUE_LOGIN_TO_RECOVER)
    }


}

