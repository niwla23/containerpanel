export default function bytesToString(input: number): string {
    let output = input.toFixed(2).toString() + "B"
    if (input >= 1000) {
        output = `${(input / 1000).toFixed(2)} kB`
    }
    if (input >= Math.pow(10, 6)) {
        output = `${(input / Math.pow(10, 6)).toFixed(2)} MB`
    }
    if (input >= Math.pow(10, 9)) {
        output = `${(input / Math.pow(10, 9)).toFixed(2)} GB`
    }
    return output
}