#! /usr/local/bin/python3
from Bio import SeqIO
from collections import Counter
import re
from itertools import dropwhile


def import_data(file_path):
    """
    Function that accept path to a .fasta file and import it into python
    """
    return SeqIO.parse(file_path, "fasta")


def count_records(fasta_dict):
    """
    Function that counts number of records in a dictionary of fasta records.
    return: integer represent number of sequences
    """
    return len(fasta_dict)


def as_dict(file_path):
    """
    Function that reads in fasta format file and
    return records as a dictionary.
    """
    return SeqIO.to_dict(import_data(file_path))


def seq_len(fasta_dict):
    """
    Function that calculates the length of each sequence in a fasta dictionary
    and returns a dictionary format id: number of characters
    """
    return {seq_id: len(fasta_dict[seq_id].seq) for seq_id in fasta_dict.keys()}


def seq_len_min_max(_dict, longest=True):
    """
    Function calculates max and min sequence length from dictionary with sequence lengths.
    It calculates longest sequence in a dictionary by default.
    """
    if longest:
        return max(_dict.values())
    else:
        return min(_dict.values())


def seq_len_min_max_id(_dict, longest=True):
    """
    Functions returns list of sequence indentifier(s) for max or min sequence length.
    """
    # get min or max sequence length
    threshold = seq_len_min_max(_dict, longest)
    return [seq_id for seq_id in _dict.keys() if _dict[seq_id] == threshold]


def find_start_codon_pos(seq, frame=1):
    """
    Function that finds position of start codons in a DNA sequence
    return list of starting indexes
    """
    return [i for i in range(frame - 1, len(seq), 3) if seq[i:i + 3] == "ATG"]


def find_stop_codon_pos(seq, frame=1):
    """
    Function that finds closest stop codon for each start codon.
    """
    return [i for i in range(frame - 1, len(seq), 3) if seq[i:i + 3] in ["TAA", "TAG", "TGA"]]


def orfs(seq, frame=1):
    """
    Function that finds all open reading frames - ORFs in a DNA sequence. 
    For different frames - starting positions.
    """
    # find start and stop indexes
    start_indexes = find_start_codon_pos(seq, frame)
    stop_indexes = find_stop_codon_pos(seq, frame)

    # for frame 1 we take whole seq, for frame 2 leave first base out and for 3rd frame
    # first 2 bases
    seq = seq[frame - 1:]
    orfs = []
    stop_index = 0

    # find ORF sequences
    for start in start_indexes:
        for stop in stop_indexes:
            # orf start is after the last stop codon and before next stop codon
            if start < stop and start > stop_index:
                orfs.append(seq[start:stop + 3])
                # move to the base after the stop codon
                stop_index += 3
                break
    return orfs


def len_orfs(seq, frame=1):
    """
    Function calculates length of each ORF in DNA sequence.
    return sorted list of tuple lengths with sequences
    """
    seq_orfs = orfs(seq, frame)
    # at least one orf
    if seq_orfs:
        return sorted([(len(s), s) for s in seq_orfs])
    return None


def longest_ORF(fasta_dict, frame=1):
    """
    Function calculates longest ORF in a fasta file disctionary
    return tuple with length, ORF and sequence ID
    """
    file_orfs = []
    for seq_id in fasta_dict.keys():
        seq = str(fasta_dict[seq_id].seq)
        seq_orfs = len_orfs(seq, frame)
        if seq_orfs != None:
            file_orfs.append((max(seq_orfs), seq_id))

    return max(file_orfs)


def longest_ORF_in_seq(fasta_dict, seq_id, frame=1):
    """
    Function calculates longest ORF in a specified sequence identifier
    return tuple with length, ORF and sequence ID
    """
    seq = str(fasta_dict[seq_id].seq)
    seq_orfs = len_orfs(seq, frame)
    # have at least one ORF
    if seq_orfs != None:
        return max(seq_orfs)[0]
    # no ORF in DNA sequence
    return None


def ORF_start_position(seq, orf):
    """
    Function that finds and returns starting index of ORF in DNA sequence.
    """
    return seq.find(orf)


def repeats(fasta_dict, n):
    """
    Function finds all repeats of length n in a given fasta file dictionary.
    returns: Counter of repeats
    """
    def drop_repeats(counter):
        """
        Function drop repeats that occured once in a sequence.
        """
        for key, count in dropwhile(lambda key_count: key_count[1] > 1, counter.most_common()):
            del counter[key]
        return counter

    all_repeats = Counter()
    # for each sequence
    for seq_id in fasta_dict.keys():
        seq = str(fasta_dict[seq_id].seq)
        # find all n mers or repeats of length n
        nmers = [seq[i:i + n] for i in range(len(seq) - n + 1)]
        # count repeats
        counter = Counter(nmers)
        # remove repeats occuring once and update repeats count
        all_repeats.update(drop_repeats(counter))

    return all_repeats


if __name__ == "__main__":
    file_path = "./dna2.fasta"
    d = as_dict(file_path)
    # How many records are in the multi-FASTA file?
    print(count_records(d))
    # What is the length of the longest sequence in the file?
    seq_len_dict = seq_len(d)
    print(seq_len_min_max(seq_len_dict))
    # What is the length of the shortest sequence in the file?
    print(seq_len_min_max(seq_len_dict, False))
    # What is the length of the longest ORF appearing in reading frame 2 of any of the sequences?
    print(longest_ORF(d, 2)[0][0])
    # What is the starting position of the longest ORF in reading frame 3 in any of the sequences?
    l_orf = longest_ORF(d, 3)
    print(ORF_start_position(str(d[l_orf[1]].seq), l_orf[0][1]))
    # What is the length of the longest ORF appearing in any sequence and in any forward reading frame?
    print(longest_ORF(d, 1)[0][0])
    # What is the length of the longest forward ORF that appears in the sequence with the identifier gi|142022655|gb|EQ086233.1|16?
    print(longest_ORF_in_seq(d, seq_id="gi|142022655|gb|EQ086233.1|16"))
    # Find the most frequently occurring repeat of length 6 in all sequences. How many times does it occur in all?
    count = repeats(d, 6)
    print(max(count.values()))
    # How many different 12-base sequences occur Max times?
    count = repeats(d, 12)
    max_12 = max(count.values())
    print(len([val for val in count.values() if val == max_12]))
    # Which one of the following repeats of length 7 has a maximum number of occurrences?
    count = repeats(d, 7)
    # key with max value
    print(max(count, key=count.get))
