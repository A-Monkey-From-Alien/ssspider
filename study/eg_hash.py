from hashlib import md5, sha1, sha224, sha256, sha384, sha512

hash_funcs = [md5, sha1, sha224, sha256, sha384, sha512]


def hash_show(pend_str):
    result = []
    for func in hash_funcs:
        s_hash_obj = func(pend_str)
        s_hash_hex = s_hash_obj.hexdigest()
        result.append((s_hash_obj.name, s_hash_hex,  len(s_hash_hex)))
    return result


if __name__ == '__main__':
    pend_str = 'Life is short, I love python'
    rs = hash_show(pend_str.encode())
    print(rs)

"""
('md5', '5e102fde11e69360992d3d4813d1f179', 32)
('sha1', '45aaedae85286e0a8d97e67bf7ee6fdecb94065e', 40)
('sha224', 'a8a9eea3d8403115dd3e5c8f6c67a0e915d7216b5648100d492ee3b7', 56)
('sha256', '1a877be25defef34721ca21e21e60cb67000343ffb698b8f555d3b8e11fc3ec1', 64)
('sha384', 'd26fa331de827ef024aeba82bd6dd0ad7f9e53623e9512a4105d5c71c4f27eebf2343bf34a99eeb59525a4a6fa4f5154', 96)
('sha512', '181983da55b08f1e606fcff6f7e74706b0580ab0cbf15341c1b241018a53e0ace6acf6177d3a42e79d7206c289be6fa9b7f5d9e9e59a762a58e318bbdf9b05ae', 128)
"""
