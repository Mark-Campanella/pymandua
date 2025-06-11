from pymandua import to_mkd
if __name__ == "__main__":
    # Example usage:
    result = to_mkd(
        urls="https://pt.wikipedia.org/wiki/Luís_XIV_de_França",
        keywords=["Luís XIV", "França", "Monarquia Absoluta"],
        wait=2,
        threshold=99
    )
    print(result)