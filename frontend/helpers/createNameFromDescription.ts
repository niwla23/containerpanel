function trimUnderscores(input: string): string {
    let splitted = input.split("_")
    let new_array: Array<string> = []
    splitted.forEach(element => {
        if (element) {
            new_array.push(element)
        }
    });
    return new_array.join("_")
}


export default function createNameFromDescription(input: string): string {
    input = input.trim()
    input = input.replace(/ä/g, "ae")
    input = input.replace(/ö/g, "oe")
    input = input.replace(/ü/g, "ue")
    input = input.replace(/[^a-zA-Z0-9_ ]/g, "_")
    input = input.replace(/\s/g, "_")
    input = input.toLowerCase()
    input = trimUnderscores(input)
    return input
}