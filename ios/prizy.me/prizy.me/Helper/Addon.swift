//
//  WordingAddon.swift
//  prizy.me
//
//  Created by Jay Rinaldi Fatalla on 2016/10/10.
//  Copyright © 2016 Jay Rinaldi Fatalla. All rights reserved.
//

import Foundation
import Foundation
import UIKit

func Localized(_ word:Wording) -> String {
    return NSLocalizedString( word.rawValue, comment: "")
}

extension UIViewController {
    func transitionTo(_ segue:Segue) {
        performSegue(withIdentifier: segue.rawValue, sender: self)
    }
}

