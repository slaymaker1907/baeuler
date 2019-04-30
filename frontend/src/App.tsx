import React, { Component, FormEvent, ReactHTML, ChangeEvent } from 'react';
//import logo from './logo.svg';
import './App.css';

interface AppState {
  piece_name: string;
  image_name?: string;
  perc_overlap: string;
}

export class App extends Component<{}, AppState> {
  public change_piece: (inp: ChangeEvent<HTMLInputElement>) => void;
  public change_overlap: (inp: ChangeEvent<HTMLInputElement>) => void;
  public get_original: () => void;
  public get_chorded: () => void;
  public get_analysis: () => void;

  constructor(props: {}) {
    super(props);
    this.state = {
      piece_name: 'bwv66.6.xml',
      perc_overlap: '30'
    };
    this.change_piece = (inp: ChangeEvent<HTMLInputElement>) => {
      this.setState({
        piece_name: inp.target.value,
        image_name: undefined
      });
    };
    this.change_overlap = (inp: ChangeEvent<HTMLInputElement>) => {
      this.setState({
        perc_overlap: inp.target.value,
        image_name: undefined
      });
    };
    const get_generic_image = (prefix: string) => () => {
      this.setState({
        image_name: `/${prefix}/${this.state.piece_name.replace('.xml', '.svg')}`
      });
    };
    this.get_original = get_generic_image('original');
    this.get_chorded = get_generic_image('chords');
    // this.get_analysis = get_generic_image('analysis');
    this.get_analysis = () => {
      this.setState({
        image_name: `/analysis/${this.state.perc_overlap}/${this.state.piece_name.replace('.xml', '.svg')}`
      });
    };
  }

  render() {
    const image_jsx = this.state.image_name ? <img src={this.state.image_name} /> : undefined;
    return (
    <div>
      <div>
        <input onChange={this.change_piece} value={this.state.piece_name} />
        <button onClick={this.get_original}>Original</button>
        <button onClick={this.get_chorded}>Chordify</button>
        <button onClick={this.get_analysis}>Topological Analysis</button>
      </div>
      <div>
        <input onChange={this.change_overlap} value={this.state.perc_overlap} />
        <label>Overlap Percentage</label>
      </div>
      <div>
        {image_jsx}
      </div>
    </div>
    );
  }
}
