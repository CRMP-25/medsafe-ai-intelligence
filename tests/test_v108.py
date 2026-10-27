import io
import csv
import zipfile
from scripts.validate_export import check,self_test

def test_offline_export_fixture():
    assert check(self_test()) == []

def test_detect_truncated_provenance():
    data=self_test()
    output=io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as source, zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED) as dest:
        for item in source.namelist():
            blob=source.read(item)
            if item=='associations.csv':
                rows=list(csv.DictReader(io.StringIO(blob.decode())))
                rows[0]['source_ids']=rows[0]['source_ids'].split(', ')[0]
                buf=io.StringIO()
                writer=csv.DictWriter(buf,fieldnames=list(rows[0]))
                writer.writeheader();writer.writerows(rows)
                blob=buf.getvalue().encode()
            dest.writestr(item,blob)
    assert any('truncated provenance' in x for x in check(output.getvalue()))
