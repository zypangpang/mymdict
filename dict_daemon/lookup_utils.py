from struct import pack
import lzo,zlib

def decode_record_by_index(filename, index_tuple, encoding=None):
    block_offset, compressed_size, decompressed_size, record_begin, record_end = index_tuple

    try:
        f = open(filename, 'rb')
    except Exception as e:
        return "Dict file open failed. Check the path"

    f.seek(block_offset)

    record_block_compressed = f.read(compressed_size)
    # 4 bytes indicates block compression type
    record_block_type = record_block_compressed[:4]

    record_block=None
    # no compression
    if record_block_type == b'\x00\x00\x00\x00':
        record_block = record_block_compressed[8:]
    # lzo compression
    elif record_block_type == b'\x01\x00\x00\x00':
        if lzo is None:
            print("LZO compression is not supported")
            raise Exception("LZO not supported")
        # decompress
        header = b'\xf0' + pack('>I', decompressed_size)
        record_block = lzo.decompress(header + record_block_compressed[8:])
    # zlib compression
    elif record_block_type == b'\x02\x00\x00\x00':
        # decompress
        record_block = zlib.decompress(record_block_compressed[8:])

    if not record_block:
        raise Exception("Parse record block error")

    record = record_block[record_begin:record_end]

    # convert to utf-8
    if encoding:
        record = record.decode(encoding, errors='ignore').strip(u'\x00')
    else:
        record = record.strip(b'\x00').decode("utf-8")

    return record