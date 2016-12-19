//: Playground - noun: a place where people can play

import UIKit

let d = "esfgfhmjdf".data(using: .utf8)

var hexstring = ""
for var c in d! {
    hexstring += String(c, radix: 16)
    
}
print(hexstring)