import React from 'react'
import { AppBar, Toolbar, Typography } from '@material-ui/core'

function Header() {
    return (
        <AppBar position="static">
            <Toolbar>
                <Typography>Living Condition Heatmap</Typography>
            </Toolbar>
        </AppBar>
    )
}

export default Header