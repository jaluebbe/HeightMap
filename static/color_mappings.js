var colorMappings = {
    elevation: {
        'surface elevation': {
            text: 'surface elevation',
            color: 'green'
        }
    },
    steepness: {
        '0': {
            text: '0-2%',
            color: '#006400'
        },
        '1': {
            text: '2-5%',
            color: '#9acd32'
        },
        '2': {
            text: '5-10%',
            color: 'yellow'
        },
        '3': {
            text: '10-20%',
            color: 'orange'
        },
        '4': {
            text: '20%+',
            color: 'red'
        }
    },
    'land cover': {
        '0': {
            color: '#000000',
            text: 'No data'
        },
        '10': {
            color: '#ffff64',
            text: 'Cropland, rainfed'
        },
        '11': {
            color: '#ffff64',
            text: 'Herbaceous cover'
        },
        '12': {
            color: '#ffff00',
            text: 'Tree or shrub cover'
        },
        '20': {
            color: '#aaf0f0',
            text: 'Cropland, irrigated or post-flooding'
        },
        '30': {
            color: '#dcf064',
            text: 'Mosaic cropland (>50%) / natural vegetation (tree, shrub, herbaceous cover) (<50%)'
        },
        '40': {
            color: '#c8c864',
            text: 'Mosaic natural vegetation (tree, shrub, herbaceous cover) (>50%) / cropland (<50%)'
        },
        '50': {
            color: '#006400',
            text: 'Tree cover, broadleaved, evergreen, closed to open (>15%)'
        },
        '60': {
            color: '#00a000',
            text: 'Tree cover, broadleaved, deciduous, closed to open (>15%)'
        },
        '61': {
            color: '#00a000',
            text: 'Tree cover, broadleaved, deciduous, closed (>40%)'
        },
        '62': {
            color: '#aac800',
            text: 'Tree cover, broadleaved, deciduous, open (15-40%)'
        },
        '70': {
            color: '#003c00',
            text: 'Tree cover, needleleaved, evergreen, closed to open (>15%)'
        },
        '71': {
            color: '#003c00',
            text: 'Tree cover, needleleaved, evergreen, closed (>40%)'
        },
        '72': {
            color: '#005000',
            text: 'Tree cover, needleleaved, evergreen, open (15-40%)'
        },
        '80': {
            color: '#285000',
            text: 'Tree cover, needleleaved, deciduous, closed to open (>15%)'
        },
        '81': {
            color: '#285000',
            text: 'Tree cover, needleleaved, deciduous, closed (>40%)'
        },
        '82': {
            color: '#286400',
            text: 'Tree cover, needleleaved, deciduous, open (15-40%)'
        },
        '90': {
            color: '#788200',
            text: 'Tree cover, mixed leaf type (broadleaved and needleleaved)'
        },
        '100': {
            color: '#8ca000',
            text: 'Mosaic tree and shrub (>50%) / herbaceous cover (<50%)'
        },
        '110': {
            color: '#be9600',
            text: 'Mosaic herbaceous cover (>50%) / tree and shrub (<50%)'
        },
        '120': {
            color: '#966400',
            text: 'Shrubland'
        },
        '121': {
            color: '#784b00',
            text: 'Shrubland evergreen'
        },
        '122': {
            color: '#966400',
            text: 'Shrubland deciduous'
        },
        '130': {
            color: '#ffb432',
            text: 'Grassland'
        },
        '140': {
            color: '#ffdcd2',
            text: 'Lichens and mosses'
        },
        '150': {
            color: '#ffebaf',
            text: 'Sparse vegetation (tree, shrub, herbaceous cover) (<15%)'
        },
        '151': {
            color: '#ffc864',
            text: 'Sparse tree (<15%)'
        },
        '152': {
            color: '#ffd278',
            text: 'Sparse shrub (<15%)'
        },
        '153': {
            color: '#ffebaf',
            text: 'Sparse herbaceous cover (<15%)'
        },
        '160': {
            color: '#00785a',
            text: 'Tree cover, flooded, fresh or brakish water'
        },
        '170': {
            color: '#009678',
            text: 'Tree cover, flooded, saline water'
        },
        '180': {
            color: '#00dc82',
            text: 'Shrub or herbaceous cover, flooded, fresh/saline/brakish water'
        },
        '190': {
            color: '#c31400',
            text: 'Urban areas'
        },
        '200': {
            color: '#fff5d7',
            text: 'Bare areas'
        },
        '201': {
            color: '#dcdcdc',
            text: 'Consolidated bare areas'
        },
        '202': {
            color: '#fff5d7',
            text: 'Unconsolidated bare areas'
        },
        '210': {
            color: '#0046c8',
            text: 'Water bodies'
        },
        '220': {
            color: '#ffffff',
            text: 'Permanent snow and ice'
        }
    }
}