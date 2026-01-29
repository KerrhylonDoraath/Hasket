def lineParse(inputLines: list[str]) -> list[list[str]]:
    """Iterates through provided strings
    to separate words by the first ": ".

    Parameters
        (list[str]) inputLines: list of strings

    Returns:    list[list [str]]
    """

    resultSet = []
    if not inputLines:
        return []
    for line in inputLines:
        scanner = ""
        mode = "keyword"
        entry = []
        for x in line:
            if x == ":" and mode == "keyword":
                mode = "parameter"

                entry.append(scanner)
                scanner = ""
                continue
            scanner += x
        if scanner[-1] == "\n":
            scanner = scanner[:-1]
        entry.append(scanner[1:])
        resultSet.append(entry)
    return resultSet
