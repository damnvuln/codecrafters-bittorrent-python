import json
import sys
from typing import Any, List, Dict


class bencodeDecoder:

    def __init__(self, bencoded_value: bytes):
        self.bencoded_value = bencoded_value
        self.index = 0

    def decode(self) -> Any:
        return self._decode_types()

    def _decode_intgr(self) -> int:
        start_index = self.index + 1
        end_index = self.bencoded_value.find(b"e", start_index)
        if end_index == -1:
            raise ValueError("'e' isn't there. Invalid Integer")
        intgr_value = int(self.bencoded_value[start_index:end_index])
        self.index = end_index + 1
        return intgr_value

    def _decode_str(self) -> str:
        fst_index = self.bencoded_value.find(b":", self.index)
        if fst_index == -1:
            raise ValueError("':' isn't there. Invalid String")
        length = int(self.bencoded_value[self.index : fst_index])
        start_index = fst_index + 1
        end_index = start_index + length
        if end_index > len(self.bencoded_value):
            raise ValueError("More length error.")
        str_value = self.bencoded_value[start_index:end_index]
        self.index = end_index
        
        try:
            return str_value.decode("utf-8")
        except UnicodeDecodeError:
            return str_value # Return the raw bytes if decoding fails

    def _decode_list(self) -> List[Any]:
        rst_list = []
        self.index += 1
        while self.index < len(self.bencoded_value) and self.bencoded_value[
            self.index
        ] != ord("e"):
            elem = self._decode_types()
            rst_list.append(elem)
        if self.index >= len(self.bencoded_value) or self.bencoded_value[
            self.index
        ] != ord("e"):
            raise ValueError("'e' missing.")
        self.index += 1
        return rst_list

    def _decode_dict(self) -> Dict[str, Any]:
        result_dict = {}
        self.index += 1
        while self.index < len(self.bencoded_value) and self.bencoded_value[
            self.index
        ] != ord("e"):
            key = self._decode_str()
            value = self._decode_types()
            result_dict[key] = value
        if self.index >= len(self.bencoded_value) or self.bencoded_value[
            self.index
        ] != ord("e"):
            raise ValueError("'e' missing. Invalid Dictionary")
        self.index += 1
        return result_dict

    def _decode_types(self) -> Any:
        if self.bencoded_value[self.index] == ord("i"):
            return self._decode_intgr()
        if self.bencoded_value[self.index] == ord("l"):
            return self._decode_list()
        if self.bencoded_value[self.index] == ord("d"):
            return self._decode_dict()
        elif chr(self.bencoded_value[self.index]).isdigit():
            return self._decode_str()
        else:
            raise NotImplementedError("Include Only Integers, String, Dict & List")

def bytes_to_str(data):
            if isinstance(data, bytes):
                try:
                    return data.decode("utf-8")
                except UnicodeDecodeError:
                    return data  
            raise TypeError(f"Type not serializable: {type(data)}")
if __name__ == "__main__":
    command = sys.argv[1]
    bencoded_inp = sys.argv[2].encode()

    if command == "decode":
        # Use bencodeDecoder to decode the value
        decoder = bencodeDecoder(bencoded_inp)
        decoded_value = decoder.decode()
        print(json.dumps(decoded_value, default=bytes_to_str))
    elif command == "info":
        file_name = sys.argv[2]
        with open(file_name, "rb") as torrent_file:
            bencoded_content = torrent_file.read()
        decoder = bencodeDecoder(bencoded_content)
        torrent = decoder.decode()
        print("Tracker URL:", torrent["announce"])  
        print("Length:", torrent["info"]["length"])
