import csv
import os.path

class AbstractStatsSaver(object):
    DATA_TYPES = (
        'food_discovered',
        'time',
        'best_finding_cost',
        'last_cost',
        'avg_pheromone',
        'max_pheromone',
        'pheromone_ratio',
    )

class NullStatsSaver(AbstractStatsSaver):
    """ does nothing """
    def add_sample(self, *args, **kwargs):
        pass

class FileStatsSaver(AbstractStatsSaver):
    DELIMITER = None # TBD
    EXTENSION = None # TBD
    def __init__(self, artifact_directory, filename_part='stats'):
        self.writer = csv.writer(
            open(
                os.path.join(
                    artifact_directory,
                    '%s.%s' % (filename_part, self.EXTENSION),
                ),
                'wb',
            ),
            delimiter=self.DELIMITER,
        )
        self.writer.writerow(self.DATA_TYPES) # header
    def add_sample(self, data):
        self.writer.writerow([data[key] for key in self.DATA_TYPES])

class CSVStatsSaver(FileStatsSaver):
    DELIMITER = ','
    EXTENSION = 'csv'

class TSVStatsSaver(FileStatsSaver):
    DELIMITER = '\t'
    EXTENSION = 'tsv'

