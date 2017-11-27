import 'app.scss';
import React from 'react';
import ReactDOM from 'react-dom';
import { Button, Image } from 'react-bootstrap';

class App extends React.Component {
    constructor() {
        super();

        this.state = {
            loading: false,
            graphs: [],
            checked: []
        };
    }

    componentDidMount() {
        this.setState({ loading: true });
        this.loadData()
            .then(data => {
                // find 1st 24h entry, select it
                let firstSel = this.findPeriodEntry(data.fileInfos, '*', '*', '24h');
                let checked = [];
                if (firstSel) {
                    checked = [firstSel];
                }
                this.setState({ loading: false, graphs: data.fileInfos, checked });
            })
            .catch(err => {
                this.setState({ loading: false, graphs: [], checked: [] });
            });
    }

    findPeriodEntry(data, setName, type, timePeriod) {
        for (let iSet = 0; iSet < data.length; iSet++) {
            if (data[iSet].setName === setName || setName === '*') {
                for (let iType = 0; iType < data[iSet].types.length; iType++) {
                    if (data[iSet].types[iType].type === type || type === '*') {
                        for (let iPeriod = 0; iPeriod < data[iSet].types[iType].periods.length; iPeriod++) {
                            if (
                                data[iSet].types[iType].periods[iPeriod].timePeriod === timePeriod ||
                                timePeriod === '*'
                            ) {
                                return data[iSet].types[iType].periods[iPeriod];
                            }
                        }
                    }
                }
            }
        }
        return null;
    }

    loadData() {
        return fetch('rrd_files', {
            method: 'GET'
        }).then(res => res.json());
    }

    toggleSelection(periodEntry) {
        let index = this.state.checked.indexOf(periodEntry);
        if (index > -1) {
            this.setState({ checked: this.state.checked.filter(item => item !== periodEntry) });
        } else {
            this.setState({ checked: this.state.checked.concat([periodEntry]) });
        }
    }

    isSelected(periodEntry) {
        return this.state.checked.indexOf(periodEntry) > -1;
    }

    createImageUrl(periodInfo) {
        return 'rrd_images/' + periodInfo.image_file + '?' + new Date().getTime();
    }

    render() {
        let { loading, graphs, checked } = this.state;
        return (
            <div className="app-container">
                <div className="navigation">
                    <h3>Graphs</h3>
                    {loading ? <div>Load ...</div> : this.renderMenu(graphs)}
                </div>
                <div className="content">
                    <h1>
                        Temperature and Humidity{' '}
                        <Button bsSize="xsmall" bsStyle="info" onClick={this.forceUpdate.bind(this, () => {})}>
                            reload
                        </Button>
                    </h1>
                    <div>
                        {checked.map(periodInfo => (
                            <div key={periodInfo.image_file}>
                                <h2>
                                    {periodInfo.setName}: {periodInfo.type}: {periodInfo.timePeriod}
                                </h2>
                                <Image src={this.createImageUrl(periodInfo)} responsive />
                            </div>
                        ))}
                    </div>
                </div>

                <footer>
                    <p>
                        &copy; 2017 <a href="https://alexi.ch/">alexi.ch</a>
                    </p>
                </footer>
            </div>
        );
    }

    renderMenu(graphs) {
        return (
            <ul>
                {graphs.map(set => (
                    <li key={set.setName}>
                        {set.setName}
                        <ul>
                            {set.types.map(type => (
                                <li key={type.type}>
                                    {type.type}
                                    <ul>
                                        {type.periods.map(period => (
                                            <li key={period.timePeriod}>
                                                <label>
                                                    <input
                                                        type="checkbox"
                                                        checked={this.isSelected(period)}
                                                        onChange={this.toggleSelection.bind(this, period)}
                                                    />{' '}
                                                    {period.timePeriod}
                                                </label>
                                            </li>
                                        ))}
                                    </ul>
                                </li>
                            ))}
                        </ul>
                    </li>
                ))}
            </ul>
        );
    }
}

ReactDOM.render(<App />, document.getElementById('app'));
