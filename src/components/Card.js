import React from 'react'

function CardDownload(props){
  let data = props.props  
  let data_dict = []
    if(data.pdf_url != "None")
      data_dict.push(<a target="_blank"  className="book-link-pdf App-link" href={data.pdf_url}>PDF({(data.pdf_size/(1024*1024)).toFixed(2)}MB)</a>)
    if(data.epub_url != "None")
      data_dict.push(<a target="_blank"  className="book-link-epub App-link" href={data.epub_url}>EPUB({(data.epub_size/(1024*1024)).toFixed(2)}MB)</a>)
    if(data.other_url != "None")
      data_dict.push(<a target="_blank"  className="book-link-epub App-link" href={data.other_url}>{data.format}({(data.other_size/(1024*1024)).toFixed(2)}MB)</a>)
    if(data_dict.length > 0){
      return (
        <React.Fragment>
          {
            data_dict.map( download_link => download_link )
          }
        </React.Fragment>
      )
    }
    else
      return ""
  }
  
  function BookCard(props){
    return(
      <div className="book-card">
        <div className="book-card-img">
            <a target="_blank" href={props.props.url}>
            {
                props.props.image != null
                ?(<img className="book-card-img-tag" src={"data:image/jpeg;base64,".concat(props.props.image)}/>)
                :(<img className="book-card-img-tag" src={props.props.image_url}/>)
            }
            </a>
        </div>
        <div className="book-card-details">
          <div className="book-card-tite">
            <span className="card-span-title"> {props.props.title} </span>
          </div>
          <div className="book-card-subtitle">
          </div>
          <div className="book-card-description">
            <span className="book-desc-span">{
              props.props.description.length > 0 ?
              props.props.description
              : "Book description not available."
            }
            </span>
          </div>
          <div className="book-card-misc">
              <span style={{'marginLeft': '0px'}}><b>Author:</b>{props.props.author.substring(0, 18)},</span>
              <span style={{'marginLeft': '5px'}}><b>Published:</b>{props.props.year},</span>
              <span style={{'marginLeft': '5px'}}><b>Pages:</b>{props.props.pages}</span>
          </div>
        </div>
        <div className="book-card-download">
          <CardDownload props={props.props} />
        </div>
      </div>
    )
  }

export default BookCard