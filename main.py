from typing import List, Dict
from src.Service.UCDMResolver import UCDMConvertedField


def get_input_files(ucdm, parameters) -> Dict[str, str]:
    return {
        "phenotype.txt": build_phenotype(ucdm, parameters['variables']),
        "nextflow.config": file_get_contents('nextflow.config'),
        "nextflow-gwas.config": get_nextflow_config(parameters['variables'], parameters['isBinary'])
    }


def get_output_file_masks(parameters) -> Dict[str, str]:
    return {
        ".nextflow.log": "/basic/.nextflow.log",
        "nextflow-gwas.config": "/nextflow-gwas.config",
        "trace-*.txt": "/basic/",
        "output/": "/output/",
    }


def get_nextflow_cmd(input_files: Dict[str, str], parameters, run_name, weblog_url):
    return "sudo chown -R nextflow .; nextflow run genepi/nf-gwas -r v1.0.4 -c nextflow-gwas.config -c nextflow.config -name {} -with-report report.html -with-weblog {} -with-trace -ansi-log".format(
        run_name,
        weblog_url,
    )


def get_nextflow_config(variables: List[str], is_binary: bool) -> str:
    is_binary_str = 'true' if is_binary else 'false'

    config = "params {\n"
    config += "  project                       = 'Unison_GWAS'\n"
    config += "  genotypes_prediction          = '/data/nextflow/data/example.{bim,bed,fam}'\n"
    config += "  genotypes_association         = '/data/nextflow/data/example.vcf.gz'\n"
    config += "  genotypes_build               = 'hg19'\n"
    config += "  genotypes_association_format  = 'vcf'\n"
    config += "  phenotypes_filename           = 'phenotype.txt'\n"
    config += "  phenotypes_columns            = '{}'\n".format(",".join(variables))
    config += "  phenotypes_binary_trait       = {}\n".format(is_binary_str)
    config += "  regenie_test                  = 'additive'\n"
    config += "  annotation_min_log10p         = 2\n"
    config += "  rsids_filename                = '/data/nextflow/data/rsids.tsv.gz'\n"
    config += "}\n"
    config += "\n"
    config += "process {\n"
    config += "   withName: '.*' {\n"
    config += "       cpus = 8\n"
    config += "       memory = 40.GB\n"
    config += "   }\n"
    config += "}\n"

    return config


def build_phenotype(ucdm: List[Dict[str, UCDMConvertedField]], variables: List[str]) -> str:
    if len(ucdm) == 0:
        return ''
    content = "FID IID " + (" ".join(variables)) + "\n"
    i = 1
    for row in ucdm:
        content += "{} {}".format(i, i)
        for key in variables:
            content += " " + convert_value(row[key].export_value)
        content += "\n"
        i += 1

    return content


def convert_value(variable) -> str:
    if isinstance(variable, bool):
        return str(int(variable))

    return str(variable)


def file_get_contents(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.read()
