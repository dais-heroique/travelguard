import SwiftUI

enum TGColor {
    static let ink = Color(red: 0.055, green: 0.12, blue: 0.18)
    static let teal = Color(red: 0.04, green: 0.52, blue: 0.55)
    static let mint = Color(red: 0.78, green: 0.95, blue: 0.91)
    static let ivory = Color(red: 0.98, green: 0.97, blue: 0.93)
    static let amber = Color(red: 0.95, green: 0.58, blue: 0.14)
    static let coral = Color(red: 0.86, green: 0.22, blue: 0.26)
    static let muted = Color(red: 0.38, green: 0.43, blue: 0.45)
}

extension View {
    func tgCard() -> some View {
        self.padding(16).background(.white).clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous)).overlay(RoundedRectangle(cornerRadius: 20, style: .continuous).stroke(Color.black.opacity(0.07)))
    }
}
