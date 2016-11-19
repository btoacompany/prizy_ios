//
//  PrizyViewController.swift
//  prizy.me
//
//  Created by Jay Rinaldi Fatalla on 2016/11/19.
//  Copyright © 2016 Jay Rinaldi Fatalla. All rights reserved.
//

import Foundation
import UIKit


public func setGradientBackground(_ view:UIView) {
    let gradient: CAGradientLayer = CAGradientLayer()
    gradient.frame = view.bounds
    
    let startColor = UIColor.init(red: 1.0, green: 0.470588, blue: 0.0, alpha: 1.0)
    let endColor = UIColor.init(red: 1.0, green: 0.764706, blue: 0.0, alpha: 1.0)
    
    gradient.colors = [startColor.cgColor, endColor.cgColor]
    gradient.startPoint = CGPoint(x:0, y:0.5)
    gradient.endPoint = CGPoint(x:1, y:0.5)
    
    view.layer.insertSublayer(gradient, at: 0)
}


class PrizyVC: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
      
        setGradientBackground(self.view)

        self.hideKeyboardWhenTappedAround()
    }
    
    private func hideKeyboardWhenTappedAround() {
        let tap: UITapGestureRecognizer = UITapGestureRecognizer(target: self, action: #selector(PrizyVC.dismissKeyboard))
        view.addGestureRecognizer(tap)
    }
    
    func dismissKeyboard() {
        view.endEditing(true)
    }
}

extension UIButton {
    func setUnderlinedTitle(_ text: String, for state:UIControlState) {
        let r = NSRange.init(location: 0, length: text.characters.count)
        
        let attribText = NSMutableAttributedString(string: text)
        attribText.addAttribute(NSLinkAttributeName, value: text, range: r)
        
        self.setAttributedTitle(attribText, for: state)
    }
}


class PrizyTextField: UITextField {
    var insetX: CGFloat = 0
    var insetY: CGFloat = 0
    
    func setDefault() {
        self.layer.cornerRadius = 4.0
        self.insetX = 15
    }
    
    override init(frame: CGRect) {
        super.init(frame: frame)
        self.setDefault()
    }
    
    required init?(coder aDecoder: NSCoder) {
        super.init(coder: aDecoder)
        self.setDefault()
    }
    
    
    
    override func textRect(forBounds bounds: CGRect) -> CGRect {
        return bounds.insetBy(dx: self.insetX, dy: self.insetY)
    }
    
    override func editingRect(forBounds bounds: CGRect) -> CGRect {
        return textRect(forBounds: bounds)
    }


}


class PrizyButton: UIButton {
    func setDefault() {
        self.layer.cornerRadius = 4.0
    }
    
    override init(frame: CGRect) {
        super.init(frame: frame)
        self.setDefault()
    }
    
    required init?(coder aDecoder: NSCoder) {
        super.init(coder: aDecoder)
        self.setDefault()
    }
    
}

