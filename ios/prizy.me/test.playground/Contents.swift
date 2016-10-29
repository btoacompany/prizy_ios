//: Playground - noun: a place where people can play

import UIKit

var str = "Hello, playground"
let components = str.components(separatedBy: ",")
let data = components.first(where: {
    value in
    return value.hasPrefix("Hello")
})

print(data)
