const path = require('path');
const fs = require('fs');
const config = require(path.join(__dirname, 'server.json'));
const express = require('express');
const app = express();

function find(arr, comparator) {
    for (let i = 0; i < arr.length; i++) {
        if (comparator(arr[i])) {
            return arr[i];
        }
    }
    return null;
}

/**
 * RRD images are stored in a directory, and have the following file name
 * scheme:
 * [set-name]_[type]_[time-period].png
 *
 * set-name: The name of the measurement set e.g. "living_room"
 * type: one of 'combined','temperature','humidity'
 * time-period: period to show, e.g. '24h' for the last 24 hours. Time comes in 'at'-style time definition.
 */
function readRRDImages() {
    return new Promise((resolve, reject) => {
        const imagePath = path.join(__dirname, config.data.rrd_image_path);
        fs.readdir(imagePath, (err, files) => {
            if (err) {
                reject(err);
            } else {
                let r = new RegExp('^(.*)_(combined|temperature|humidity)_(.*).png$');
                let fileMatches = files
                    .map(f => f.match(r))
                    .filter(match => match)
                    .map(match => ({
                        image_file: match[0],
                        setName: match[1],
                        type: match[2],
                        timePeriod: match[3]
                    }));
                resolve(fileMatches);
            }
        });
    });
}

function rrdTreeFromFileInfos() {
    return readRRDImages().then(fileInfos => {
        let result = [];
        fileInfos.forEach(fInfo => {
            let setEntry = find(result, item => item.setName === fInfo.setName);
            if (!setEntry) {
                setEntry = {
                    setName: fInfo.setName,
                    types: []
                };
                result.push(setEntry);
            }

            let typeEntry = find(setEntry.types, item => item.type === fInfo.type);
            if (!typeEntry) {
                typeEntry = { setName: fInfo.setName, type: fInfo.type, periods: [] };
                setEntry.types.push(typeEntry);
            }

            let periodEntry = find(typeEntry.periods, item => item.timePeriod === fInfo.timePeriod);
            if (!periodEntry) {
                periodEntry = {
                    setName: fInfo.setName,
                    type: fInfo.type,
                    timePeriod: fInfo.timePeriod,
                    image_file: fInfo.image_file
                };
                typeEntry.periods.push(periodEntry);
            }
        });
        return result;
    });
}

// ---------------- Sever and route configs -------------------
app.get('/', (req, res) => res.redirect(301, '/index.html'));
app.use(express.static('web/static'));
app.use('/rrd_images', express.static('output'));

app.get('/rrd_files', (req, res) => {
    rrdTreeFromFileInfos()
        .then(fileInfos => {
            res.json({ fileInfos });
        })
        .catch(err => {
            console.log(err);
            res.status(500).json({ error: err });
        });
});

const port = config.server.port;
app.listen(port, () => console.log(`Server is listening on port ${port}!`));
