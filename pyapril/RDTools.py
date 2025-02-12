import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

import plotly.graph_objects as go

def export_rd_matrix_img(fname, rd_matrix, max_Doppler, 
                         ref_point_range_index=0, 
                         ref_point_Doppler_index=0, 
                         box_color=None,
                         box_size=0,
                         dyn_range=None,
                         dpi=200, 
                         interpolation='sinc', 
                         cmap='jet'):
    """
        Description:
        ------------
        This function exports the given range-Doppler matrix into an image file.
        On the exported figure the X axis will represent the bistatic range while Y axis
        will show the Doppler frequencies. The Doppler ticks are automatically generated,
        but the caller should specifiy the maximum Doppler frequency in [Hz].
        
        If requested the function can draw an adition highligh box onto the exported
        range-Doppler map image. This feature is usefull when the user want to highlight
        a specific reflection. The color and the size of the highlight box is configurable
        via the 'box_color' and the 'box_size' paramters. The position of the box could be
        set by the By default, the highlight box is 
        not drawn. 
    
        In case the dynamic range paramter is not specified the function will automatically
        estimate the usefull dynamic range of the range-Doppler matrix.
        
        Parameters:
        -----------
        :param: fname                  : Filname into which the range-Doppler matrix will be exported
        :param: rd_matrix              : range-Doppler matrix to be exported
        :param: max_Doppler            : Maximum Doppler frequency in the range-Doppler matrix
        :param: ref_point_range_index  : (default: 0)
        :param: ref_point_Doppler_index: (default: 0)
        :param: box_color              : (default: None - Highlight box will not be drawn)
        :param: box_size               : (default: 0  - Highlight box will not be drawn)
        :param: dyn_range              : (default: None - Dynamic range will be automatically calculated)
        :param: dpi                    : (default: 200)
        :param: interpolation          : (default: 'sinc')
        :param: cmap                   : (default: 'jet')

            
        :type: fname                  : string
        :type: rd_matrix              : R x D complex numpy array
        :type: max_Doppler            : int
        :type: ref_point_range_index  : int
        :type: ref_point_Doppler_index: int
        :type: box_color              : string
        :type: box_size               : int
        :type: dyn_range              : float
        :type: dpi                    : int
        :type: interpolation          : string - matplotlib compatible e.q.:'sinc' / 'none'
        :type: cmap                   : string - matplotlib colormap e.g.:'jet' 

            
        Return values:
        --------------
        No return values
    """
    
    """
    --------------------------------
               Parameters
    --------------------------------
    """

    # Constant conversion parameters
    # -> Figure size
    w = 1920/250
    h = 1080/250
    
    # -> For dynamic range estimation
    range_cell_index = 20
    doppler_cell_index= 30 
    window_length=5
    window_width=5

    
    """
    --------------------------------
        Dynamic range compression
    --------------------------------
    """
    if dyn_range is None:
        # Noise floor estimation
        noise_floor = 0  # Cumulative sum of the environment power
        cell_counter = 0
        
        rd_matrix /= np.max(np.abs(rd_matrix))
        
        for wi in np.arange(-window_length, window_length + 1):
            for wj in np.arange(-window_width, window_width + 1):
                cell_counter += 1
                noise_floor += np.abs(rd_matrix[doppler_cell_index + wj, range_cell_index + wi]) ** 2
        
        noise_floor /= cell_counter  # Normalize for average calc
        dyn_range = -10*np.log10(noise_floor)

    
    rd_matrix = 10 * np.log10(np.abs(rd_matrix) ** 2)
    rd_matrix -= np.max(rd_matrix)

    for i in range(np.shape(rd_matrix)[0]):  # Remove extreme low values
        for j in range(np.shape(rd_matrix)[1]):
            if rd_matrix[i, j] < -dyn_range:
                rd_matrix[i, j] = -dyn_range
                
    """
    --------------------------------
            Display and save
    --------------------------------
    """

    plt.ioff()

    rd_fig, rd_axes = plt.subplots()
    rd_fig.set_size_inches(w,h)

    rd_plot = rd_axes.imshow(rd_matrix, interpolation=interpolation, cmap=cmap, origin='lower', aspect='auto')
    plt.ion()

    rd_axes.set_xlabel("Bistatic range cell")
    rd_axes.set_ylabel("Doppler Frequency [Hz]")
    rd_fig.colorbar(rd_plot)
    
    
    rd_axes.set_yticks(np.arange(0, np.size(rd_matrix, 0) + np.size(rd_matrix, 0) / 10, np.size(rd_matrix, 0) / 10))    
    labels = []
    labels_float = np.arange(-max_Doppler, max_Doppler + 2 * max_Doppler / 10, 2 * max_Doppler / 10).tolist()
    for label_float in labels_float:
        labels.append("{:.1f}".format(label_float))
    rd_axes.set_yticklabels(labels)
    
    
    # Draw reference square if requested
    if box_color is not None and box_size != 0:
        rd_axes.add_patch(patches.Rectangle(
            (ref_point_range_index - box_size, ref_point_Doppler_index - box_size),   # (x,y)
            (box_size*2+1),          # width
            (box_size*2+1),          # height
            fill=False,
            edgecolor = box_color,
            linewidth = 1))

    plt.tight_layout()
    rd_fig.savefig(fname, dpi=dpi)
    plt.close()
    
def plot_rd_matrix(rd_matrix,  
                   dyn_range=None,
                   interpolation='best', 
                   cmap='jet', **kwargs):
    """
        Description:
        ------------
        This function creates a plotly figure object from a given range-Doppler matrix.
        The axis of the generated figure object is scaled both in terms of bistatic range
        and Doppler frequency.
        The Doppler ticks are automatically generated, but the caller should specifiy
        the maximum Doppler frequency in [Hz] through kwargs.
        In case the user specifies the sampling frequency of the processed signal as well (fs)
        (through kwagrs) the time delay axis of the figure object will be scaled bistatic range.
            
        In case the dynamic range paramter is not specified the function will automatically
        estimate the usefull dynamic range of the range-Doppler matrix.
        
        Parameters:
        -----------
        :param: rd_matrix              : range-Doppler matrix to be exported        
        :param: dyn_range              : (default: None - Dynamic range will be automatically calculated)
        :param: interpolation          : (default: 'sinc')
        :param: cmap                   : Colormap (default: 'jet')
            
        :type: rd_matrix              : R x D complex numpy array
        :type: max_Doppler            : int
        :type: dyn_range              : float
        :type: interpolation          : string - Plotly hetamp smooth mode 'fast'/'best'/'False' (default='best')
        :type: cmap                   : string - Plotly colormap e.g.:'jet' 
        
         **kwargs
        Additional display option can be specified throught the **kwargs interface
        Valid keys are the followings:
        
        :key:               max_Doppler: Maximum Doppler frequency in the range-Doppler matrix
        :key:                        fs: sampling frequency of the processed signal   
        :type:              max_Doppler: float
        :type:                       fs: float
        
        
        Return values:
        --------------
        :return: fig: Generated range-Doppler matrix figure
        :rtype:  fig: Plotly compatibile Figure object
    
    """    
        
    """
    --------------------------------
               Parameters
    --------------------------------
    """
        
    fs          = kwargs.get('fs')
    max_Doppler = kwargs.get('max_Doppler')    
    
    # -> For dynamic range estimation
    range_cell_index = 20
    doppler_cell_index= 10 
    window_length=5
    window_width=5
    
    """
    --------------------------------
        Dynamic range compression
    --------------------------------
    """
    if dyn_range is None:
        # Noise floor estimation
        noise_floor = 0  # Cumulative sum of the environment power
        cell_counter = 0
        
        rd_matrix /= np.max(np.abs(rd_matrix))
        
        for wi in np.arange(-window_length, window_length + 1):
            for wj in np.arange(-window_width, window_width + 1):
                cell_counter += 1
                noise_floor += np.abs(rd_matrix[doppler_cell_index + wj, range_cell_index + wi]) ** 2
        
        noise_floor /= cell_counter  # Normalize for average calc
        dyn_range = -10*np.log10(noise_floor)

    
    rd_matrix = 10 * np.log10(np.abs(rd_matrix) ** 2)
    rd_matrix -= np.max(rd_matrix)

    for i in range(np.shape(rd_matrix)[0]):  # Remove extreme low values
        for j in range(np.shape(rd_matrix)[1]):
            if rd_matrix[i, j] < -dyn_range:
                rd_matrix[i, j] = -dyn_range
                
    """
    --------------------------------
            Generate Figure
    --------------------------------
    """
    
    # Prepare scales
    bistat_range_scale = np.arange(np.size(rd_matrix,1), dtype=float)
    doppler_scale      = np.arange(np.size(rd_matrix,0), dtype=float)
    x_axis_title = "Bistatic range [bin]"
    y_axis_title = "Doppler frequency [bin]"
    if fs is not None:
        bistat_range_scale *= (3*10**8/fs)/10**3
        x_axis_title = "Bistatic range [km]"
    if max_Doppler is not None:
        doppler_scale = np.linspace(-max_Doppler,max_Doppler, np.size(rd_matrix,0))
        y_axis_title = "Doppler frequency [Hz]"
    # Prepare figure object
    fig = go.Figure()       
    fig.add_trace(go.Heatmap(x=bistat_range_scale,
                             y=doppler_scale,
                             z=rd_matrix,
                             colorscale=cmap,
                             zsmooth = interpolation))
    fig.update_xaxes(title_text=x_axis_title)
    fig.update_yaxes(title_text=y_axis_title)  
    
    
    return fig

def plot_Doppler_slice(rd_matrix, bistat_range, **kwargs):
    """
        Description:
        ------------
        Displays the requested range slice of a given range-Doppler map.
        In case the sampling frequency is specified through the kwargs parameter ('fs')
        the requested range parameter is interpreted as bistatic range in [m], otherwise
        it is interpreted as [bin]
        
        When a Plotly combatible figure object is passed through the 'fig' keyword,
        the function will plot the extracted slice onto this figure, thus enabling
        multiple slices to plot on the same figure object.
        
        
        Parameters:
        -----------
        :param: rd_matrix              : range-Doppler matrix to be exported        
        :param: bistat_range           : range index, either [bin] or [m]
            
        :type: rd_matrix              : R x D complex numpy array
        :type: bistat_range           : float
        
         **kwargs
        Additional display option can be specified throught the **kwargs interface
        Valid keys are the followings:
        
        
        :key:           fs: sampling frequency of the processed signal 
        :key:  max_Doppler: Maximum Doppler frequency
        :key:          fig: Figure objet to plot on

        :type:          fs: float
        :type: max_Doppler: float
        :type:         fig: Plotly figure object
       
        
        Return values:
        --------------
        :return: fig: Generated Doppler slice figure
        :rtype:  fig: Plotly compatibile Figure object
    
    """    
        
    """
    --------------------------------
               Parameters
    --------------------------------
    """
        
    fs          = kwargs.get('fs')     
    max_Doppler = kwargs.get('max_Doppler')    
    fig         = kwargs.get('fig')
    rd_matrix = 10 * np.log10(np.abs(rd_matrix) ** 2)    

                
    """
    --------------------------------
            Generate Figure
    --------------------------------
    """    
    if bistat_range < 0:
        print("ERROR: Bistatic range should be a positive number{:.1f}".format(bistat_range))
        return None

    if fs is not None:
        d =  3*10**8/fs
        if bistat_range > (np.size(rd_matrix,1)-1)*d:
            print("ERROR: Bistatic range is out of range. {:.1f} > Max bistatic range: {:.1f} m".format(bistat_range, np.size(rd_matrix,1)*d))
            return None

        bistat_range=np.argmin(abs((np.arange(np.size(rd_matrix,1))*d-bistat_range)))

    if bistat_range > np.size(rd_matrix,1)-1:
        print("ERROR: Bistatic range is out of range. {:.1f}, Range size: {:.1f} bin".format(bistat_range, np.size(rd_matrix,1)))
        return None
    
    # Prepare scales
    doppler_scale = np.arange(np.size(rd_matrix,0), dtype=float)
    name          = "Bistatic range bin: {:d}".format(bistat_range)
    x_axis_title = "Doppler frequency [bin]"
    if max_Doppler is not None:
        doppler_scale = np.linspace(-max_Doppler,max_Doppler, np.size(rd_matrix,0))
        x_axis_title = "Doppler frequency [Hz]"
    

    # Prepare figure object
    if fig is None:        
        fig = go.Figure()      

    fig.add_trace(go.Scatter(x=doppler_scale, y=rd_matrix[:,bistat_range], name=name))
    fig.update_xaxes(title_text=x_axis_title)
    fig.update_yaxes(title_text="Amplitude [dB]")
        
    return fig

def plot_range_slice(rd_matrix, Doppler_freq, **kwargs):
    """
        Description:
        ------------
        Displays the requested range slice of a given range-Doppler map.
        In case the Doppler resolutionis specified through the kwargs parameter ('fD_res')
        the requested Doppler slice parameter is interpreted as Hz, otherwise
        it is interpreted as [bin]
        
        When a Plotly combatible figure object is passed through the 'fig' keyword,
        the function will plot the extracted slice onto this figure, thus enabling
        multiple slices to plot on the same figure object.
        
        Parameters:
        -----------
        :param: rd_matrix              : range-Doppler matrix to be exported        
        :param: Doppler_freq           : Doppler frequency index, either [bin] or [Hz]
            
        :type: rd_matrix              : R x D complex numpy array
        :type: Doppler_freq           : float
        
         **kwargs
        Additional display option can be specified throught the **kwargs interface
        Valid keys are the followings:
        
        
        :key:   fs: sampling frequency of the processed signal   
        :key:  fig: Figure objet to plot on
        :type:  fs: float
        :type: fig: Plotly figure object
        
        
        Return values:
        --------------
        :return: fig: Generated range slice figure
        :rtype:  fig: Plotly compatibile Figure object
    
    """    
        
    """
    --------------------------------
               Parameters
    --------------------------------
    """
        
    fs          = kwargs.get('fs')
    max_Doppler = kwargs.get('max_Doppler')    
    fig         = kwargs.get('fig')    
    rd_matrix = 10 * np.log10(np.abs(rd_matrix) ** 2)    

    """
    --------------------------------
            Generate Figure
    --------------------------------
    """
    if max_Doppler is not None:
        if abs(Doppler_freq) > max_Doppler:
            print("ERROR: Doppler frequency is out of range. {:.1f} > Max Doppler: {:.1f} Hz".format(Doppler_freq, max_Doppler))
            return None

        Doppler_scale = np.linspace(-max_Doppler,max_Doppler, np.size(rd_matrix,0))
        Doppler_freq=np.argmin(abs((Doppler_scale-Doppler_freq)))
    
    if Doppler_freq > np.size(rd_matrix,0)-1:
        print("ERROR: Doppler frequency is out of range. {:d}, Doppler size: {:d} bin".format(Doppler_freq, np.size(rd_matrix,0)))
        return None

    if Doppler_freq < 0:
        print("ERROR: Doppler frequency is out of range. {:d}, Doppler size: {:d} bin".format(Doppler_freq, np.size(rd_matrix,0)))
        return None
        
    bistat_range_scale = np.arange(np.size(rd_matrix,1), dtype=float)
    name = "Doppler bin: {:d}".format(Doppler_freq)
    x_axis_title = "Bistatic range [bin]"
    if fs is not None:
        bistat_range_scale *= (3*10**8/fs)/10**3
        x_axis_title = "Bistatic range [km]"

    # Prepare figure object
    if fig is None:        
        fig = go.Figure()      
    fig.add_trace(go.Scatter(x=bistat_range_scale, y=rd_matrix[Doppler_freq,:], name=name))
    fig.update_xaxes(title_text=x_axis_title)
    fig.update_yaxes(title_text="Amplitude [dB]")
        
    return fig