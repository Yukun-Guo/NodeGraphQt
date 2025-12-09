#!/usr/bin/python
from Qt import QtCore, QtWidgets, QtGui

from NodeGraphQt.constants import ViewerEnum, Z_VAL_NODE_WIDGET
from NodeGraphQt.errors import NodeWidgetError


class _NodeGroupBox(QtWidgets.QGroupBox):

    def __init__(self, label, parent=None):
        super(_NodeGroupBox, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(0)
        self.setTitle(label)

    def setTitle(self, text):
        margin = (0, 0, 0, 0)
        self.layout().setContentsMargins(*margin)
        super(_NodeGroupBox, self).setTitle(text)

    def setTitleAlign(self, align='center'):
        text_color = tuple(map(lambda i, j: i - j, (255, 255, 255),
                               ViewerEnum.BACKGROUND_COLOR.value))
        style_dict = {
            'QGroupBox': {
                'background-color': 'rgba(0, 0, 0, 0)',
                'border': '0px solid rgba(0, 0, 0, 0)',
                'margin-top': '0px',
                'padding-bottom': '0px',
                'padding-left': '1px',
                'padding-right': '1px',
                'font-size': '8pt',
            },
            'QGroupBox::title': {
                'subcontrol-origin': 'margin',
                'subcontrol-position': 'top center',
                'color': 'rgba({0}, {1}, {2}, 230)'.format(*text_color),
                'padding': '0px',
            }
        }
        if self.title():
            style_dict['QGroupBox']['padding-top'] = '12px'
        else:
            style_dict['QGroupBox']['padding-top'] = '0px'

        if align == 'center':
            style_dict['QGroupBox::title']['subcontrol-position'] = 'top center'
        elif align == 'left':
            style_dict['QGroupBox::title']['subcontrol-position'] += 'top left'
            style_dict['QGroupBox::title']['margin-left'] = '4px'
        elif align == 'right':
            style_dict['QGroupBox::title']['subcontrol-position'] += 'top right'
            style_dict['QGroupBox::title']['margin-right'] = '4px'
        stylesheet = ''
        for css_class, css in style_dict.items():
            style = '{} {{\n'.format(css_class)
            for elm_name, elm_val in css.items():
                style += '  {}:{};\n'.format(elm_name, elm_val)
            style += '}\n'
            stylesheet += style
        self.setStyleSheet(stylesheet)

    def add_node_widget(self, widget):
        self.layout().addWidget(widget)

    def get_node_widget(self):
        return self.layout().itemAt(0).widget()


class NodeBaseWidget(QtWidgets.QGraphicsProxyWidget):
    """
    This is the main wrapper class that allows a ``QtWidgets.QWidget`` to be
    added in a :class:`NodeGraphQt.BaseNode` object.

    .. inheritance-diagram:: NodeGraphQt.NodeBaseWidget
        :parts: 1

    Args:
        parent (NodeGraphQt.BaseNode.view): parent node view.
        name (str): property name for the parent node.
        label (str): label text above the embedded widget.
    """

    value_changed = QtCore.Signal(str, object)
    """
    Signal triggered when the ``value`` attribute has changed.
    
    (This is connected to the :meth: `BaseNode.set_property` function when the 
    widget is added into the node.)

    :parameters: str, object
    :emits: property name, propety value
    """

    def __init__(self, parent=None, name=None, label=''):
        super(NodeBaseWidget, self).__init__(parent)
        self.setZValue(Z_VAL_NODE_WIDGET)
        self._name = name
        self._label = label
        self._node = None

    def setToolTip(self, tooltip):
        tooltip = tooltip.replace('\n', '<br/>')
        tooltip = '<b>{}</b><br/>{}'.format(self.get_name(), tooltip)
        super(NodeBaseWidget, self).setToolTip(tooltip)

    def on_value_changed(self, *args, **kwargs):
        """
        This is the slot function that
        Emits the widgets current :meth:`NodeBaseWidget.value` with the
        :attr:`NodeBaseWidget.value_changed` signal.

        Args:
            args: not used.
            kwargs: not used.

        Emits:
            str, object: <node_property_name>, <node_property_value>
        """
        self.value_changed.emit(self.get_name(), self.get_value())

    @property
    def type_(self):
        """
        Returns the node widget type.

        Returns:
            str: widget type.
        """
        return str(self.__class__.__name__)

    @property
    def node(self):
        """
        Returns the node object this widget is embedded in.
        (This will return ``None`` if the widget has not been added to
        the node yet.)

        Returns:
            NodeGraphQt.BaseNode: parent node.
        """
        return self._node

    def get_icon(self, name):
        """
        Returns the default icon from the Qt framework.

        Returns:
            str: icon name.
        """
        return self.style().standardIcon(QtWidgets.QStyle.StandardPixmap(name))

    def get_name(self):
        """
        Returns the parent node property name.

        Returns:
            str: property name.
        """
        return self._name

    def set_name(self, name):
        """
        Set the property name for the parent node.

        Important:
            The property name must be set before the widget is added to
            the node.

        Args:
            name (str): property name.
        """
        if not name:
            return
        if self.node:
            raise NodeWidgetError(
                'Can\'t set property name widget already added to a Node'
            )
        self._name = name

    def get_value(self):
        """
        Returns the widgets current value.

        You must re-implement this property to if you're using a custom widget.

        Returns:
            str: current property value.
        """
        raise NotImplementedError

    def set_value(self, text):
        """
        Sets the widgets current value.

        You must re-implement this property to if you're using a custom widget.

        Args:
            text (str): new text value.
        """
        raise NotImplementedError

    def get_custom_widget(self):
        """
        Returns the embedded QWidget used in the node.

        Returns:
            QtWidgets.QWidget: nested QWidget
        """
        widget = self.widget()
        return widget.get_node_widget()

    def set_custom_widget(self, widget):
        """
        Set the custom QWidget used in the node.

        Args:
            widget (QtWidgets.QWidget): custom.
        """
        if self.widget():
            raise NodeWidgetError('Custom node widget already set.')
        group = _NodeGroupBox(self._label)
        group.add_node_widget(widget)
        self.setWidget(group)

    def get_label(self):
        """
        Returns the label text displayed above the embedded node widget.

        Returns:
            str: label text.
        """
        return self._label

    def set_label(self, label=''):
        """
        Sets the label text above the embedded widget.

        Args:
            label (str): new label ext.
        """
        if self.widget():
            self.widget().setTitle(label)
        self._label = label


class NodeComboBox(NodeBaseWidget):
    """
    Displays as a ``QComboBox`` in a node.

    .. inheritance-diagram:: NodeGraphQt.widgets.node_widgets.NodeComboBox
        :parts: 1

    .. note::
        `To embed a` ``QComboBox`` `in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_combo_menu`
    """

    def __init__(self, parent=None, name='', label='', items=None):
        super(NodeComboBox, self).__init__(parent, name, label)
        self.setZValue(Z_VAL_NODE_WIDGET + 1)
        combo = QtWidgets.QComboBox()
        combo.setMinimumHeight(24)
        combo.addItems(items or [])
        combo.currentIndexChanged.connect(self.on_value_changed)
        combo.clearFocus()
        self.set_custom_widget(combo)

    @property
    def type_(self):
        return 'ComboNodeWidget'

    def get_value(self):
        """
        Returns the widget current text.

        Returns:
            str: current text.
        """
        combo_widget = self.get_custom_widget()
        return str(combo_widget.currentText())

    def set_value(self, text=''):
        combo_widget = self.get_custom_widget()
        if type(text) is list:
            combo_widget.clear()
            combo_widget.addItems(text)
            return
        if text != self.get_value():
            index = combo_widget.findText(text, QtCore.Qt.MatchExactly)
            combo_widget.setCurrentIndex(index)

    def add_item(self, item):
        combo_widget = self.get_custom_widget()
        combo_widget.addItem(item)

    def add_items(self, items=None):
        if items:
            combo_widget = self.get_custom_widget()
            combo_widget.addItems(items)

    def all_items(self):
        combo_widget = self.get_custom_widget()
        return [combo_widget.itemText(i) for i in range(combo_widget.count())]

    def sort_items(self, reversed=False):
        items = sorted(self.all_items(), reverse=reversed)
        combo_widget = self.get_custom_widget()
        combo_widget.clear()
        combo_widget.addItems(items)

    def clear(self):
        combo_widget = self.get_custom_widget()
        combo_widget.clear()


class NodeLineEdit(NodeBaseWidget):
    """
    Displays as a ``QLineEdit`` in a node.

    .. inheritance-diagram:: NodeGraphQt.widgets.node_widgets.NodeLineEdit
        :parts: 1

    .. note::
        `To embed a` ``QLineEdit`` `in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_text_input`
    """

    def __init__(self, parent=None, name='', label='', text='', placeholder_text=''):
        super(NodeLineEdit, self).__init__(parent, name, label)
        bg_color = ViewerEnum.BACKGROUND_COLOR.value
        text_color = tuple(map(lambda i, j: i - j, (255, 255, 255),
                               bg_color))
        text_sel_color = text_color
        style_dict = {
            'QLineEdit': {
                'background': 'rgba({0},{1},{2},20)'.format(*bg_color),
                'border': '1px solid rgb({0},{1},{2})'
                          .format(*ViewerEnum.ITEM_BORDER_COLOR.value),
                'border-radius': '3px',
                'color': 'rgba({0},{1},{2},230)'.format(*text_color),
                'selection-background-color': 'rgba({0},{1},{2},100)'
                                              .format(*text_sel_color),
            }
        }
        stylesheet = ''
        for css_class, css in style_dict.items():
            style = '{} {{\n'.format(css_class)
            for elm_name, elm_val in css.items():
                style += '  {}:{};\n'.format(elm_name, elm_val)
            style += '}\n'
            stylesheet += style
        ledit = QtWidgets.QLineEdit()
        ledit.setText(text)
        ledit.setPlaceholderText(placeholder_text)
        ledit.setStyleSheet(stylesheet)
        ledit.setAlignment(QtCore.Qt.AlignCenter)
        ledit.editingFinished.connect(self.on_value_changed)
        ledit.clearFocus()
        self.set_custom_widget(ledit)
        self.widget().setMaximumWidth(140)

    @property
    def type_(self):
        return 'LineEditNodeWidget'

    def get_value(self):
        """
        Returns the widgets current text.

        Returns:
            str: current text.
        """
        return str(self.get_custom_widget().text())

    def set_value(self, text=''):
        """
        Sets the widgets current text.

        Args:
            text (str): new text.
        """
        if text != self.get_value():
            self.get_custom_widget().setText(text)
            self.on_value_changed()

class NodeTextEdit(NodeBaseWidget):
    """
    Displays as a ``QTextEdit`` in a node.

    .. inheritance-diagram:: NodeGraphQt.widgets.node_widgets.NodeTextEdit
        :parts: 1

    .. note::
        `To embed a` ``QTextEdit`` `in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_text_input`
    """

    def __init__(self, parent=None, name='', label='', text='', placeholder_text=''):
        super(NodeTextEdit, self).__init__(parent, name, label)
        bg_color = ViewerEnum.BACKGROUND_COLOR.value
        text_color = tuple(map(lambda i, j: i - j, (255, 255, 255),
                               bg_color))
        text_sel_color = text_color
        style_dict = {
            'QTextEdit': {
                'background': 'rgba({0},{1},{2},20)'.format(*bg_color),
                'border': '1px solid rgb({0},{1},{2})'
                          .format(*ViewerEnum.ITEM_BORDER_COLOR.value),
                'border-radius': '3px',
                'color': 'rgba({0},{1},{2},230)'.format(*text_color),
                'selection-background-color': 'rgba({0},{1},{2},100)'
                                              .format(*text_sel_color),
            }
        }
        stylesheet = ''
        for css_class, css in style_dict.items():
            style = '{} {{\n'.format(css_class)
            for elm_name, elm_val in css.items():
                style += '  {}:{};\n'.format(elm_name, elm_val)
            style += '}\n'
            stylesheet += style
        ledit = QtWidgets.QTextEdit()
        ledit.setText(text)
        ledit.setPlaceholderText(placeholder_text)
        ledit.setStyleSheet(stylesheet)
        ledit.setAlignment(QtCore.Qt.AlignCenter)
        ledit.textChanged.connect(self.on_value_changed)
        ledit.clearFocus()
        self.set_custom_widget(ledit)
        self.widget().setMaximumWidth(140)

    @property
    def type_(self):
        return 'LineEditNodeWidget'

    def get_value(self):
        """
        Returns the widgets current text.

        Returns:
            str: current text.
        """
        return str(self.get_custom_widget().toPlainText())

    def set_value(self, text=''):
        """
        Sets the widgets current text.

        Args:
            text (str): new text.
        """
        if text != self.get_value():
            self.get_custom_widget().setText(text)
            self.on_value_changed()


class NodeButton(NodeBaseWidget):
    """
    Displays as a ``QPushButton`` in a node.

    .. inheritance-diagram:: NodeGraphQt.widgets.node_widgets.NodeButton
        :parts: 1

    .. note::
        `To embed a` ``QPushButton`` `in a node, you would typically use a
        helper function like` :meth:`NodeGraphQt.BaseNode.add_button`
    """

    def __init__(self, parent=None, name='', label='', text=''):
        super(NodeButton, self).__init__(parent, name, label)

        # Create the core QPushButton widget.
        self._button = QtWidgets.QPushButton(text)

        # --- Styling ---
        # Calculate text color based on the viewer's background for good contrast.
        text_color = tuple(map(lambda i, j: i - j, (255, 255, 255),
                               ViewerEnum.BACKGROUND_COLOR.value))
        
        # Define a clean, modern stylesheet for the button.
        style_dict = {
            'QPushButton': {
                'background-color': 'rgba(40, 40, 40, 200)',
                'border': '1px solid rgba(100, 100, 100, 255)',
                'border-radius': '3px',
                'color': 'rgba({0},{1},{2},230)'.format(*text_color),
                'font-size': '10pt',
                'padding': '2px 15px',
                'max-height': '20px',
            },
            'QPushButton:hover': {
                'background-color': 'rgba(50, 50, 50, 220)',
                'border': '1px solid rgba(150, 150, 150, 255)',
            },
            'QPushButton:pressed': {
                'background-color': 'rgba(25, 25, 25, 200)',
                'border': '1px solid rgba(80, 80, 80, 255)',
            }
        }

        # Apply the stylesheet.
        stylesheet = ''
        for css_class, css in style_dict.items():
            style = '{} {{\n'.format(css_class)
            for elm_name, elm_val in css.items():
                style += '  {}:{};\n'.format(elm_name, elm_val)
            style += '}\n'
            stylesheet += style
        self._button.setStyleSheet(stylesheet)
        
        # --- Signal Connection ---
        # When the button is clicked, it will trigger the base widget's
        # 'on_value_changed' method, which in turn emits the 'value_changed'
        # signal that the node can listen to.
        self._button.clicked.connect(self.on_value_changed)

        # Embed the styled button into the node widget layout.
        self.set_custom_widget(self._button)

    @property
    def type_(self):
        """
        Returns the unique type identifier for this widget.
        """
        return 'ButtonNodeWidget'

    def get_value(self):
        """
        Returns the current text of the button.
        """
        return self._button.text()

    def set_value(self, text):
        """
        Sets the text displayed on the button.
        """
        self._button.setText(text)

class NodeCheckBox(NodeBaseWidget):
    """
    Displays as a ``QCheckBox`` in a node.

    .. inheritance-diagram:: NodeGraphQt.widgets.node_widgets.NodeCheckBox
        :parts: 1

    .. note::
        `To embed a` ``QCheckBox`` `in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_checkbox`
    """

    def __init__(self, parent=None, name='', label='', text='', state=False):
        super(NodeCheckBox, self).__init__(parent, name, label)
        _cbox = QtWidgets.QCheckBox(text)
        text_color = tuple(map(lambda i, j: i - j, (255, 255, 255),
                               ViewerEnum.BACKGROUND_COLOR.value))
        style_dict = {
            'QCheckBox': {
                'color': 'rgba({0},{1},{2},230)'.format(*text_color),
                'font-size': '10pt',
            }
        }
        stylesheet = ''
        for css_class, css in style_dict.items():
            style = '{} {{\n'.format(css_class)
            for elm_name, elm_val in css.items():
                style += '  {}:{};\n'.format(elm_name, elm_val)
            style += '}\n'
            stylesheet += style
        _cbox.setStyleSheet(stylesheet)
        _cbox.setChecked(state)
        _cbox.setMinimumWidth(80)
        font = _cbox.font()
        font.setPointSize(10)
        _cbox.setFont(font)
        _cbox.stateChanged.connect(self.on_value_changed)
        self.set_custom_widget(_cbox)
        self.widget().setMaximumWidth(140)

    @property
    def type_(self):
        return 'CheckboxNodeWidget'

    def get_value(self):
        """
        Returns the widget checked state.

        Returns:
            bool: checked state.
        """
        return self.get_custom_widget().isChecked()

    def set_value(self, state=False):
        """
        Sets the widget checked state.

        Args:
            state (bool): check state.
        """
        if state != self.get_value():
            self.get_custom_widget().setChecked(state)


class NodeSpinner(NodeBaseWidget):
    """
    Displays as a ``QSpinBox`` in a node.

    .. inheritance-diagram:: NodeGraphQt.widgets.node_widgets.NodeSpinner
        :parts: 1

    .. note::
        `To embed a` ``QSpinBox`` `in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_spinner`
    """

    def __init__(self, parent=None, name='', label='', value=0, min_val=0,
                 max_val=100):
        super(NodeSpinner, self).__init__(parent, name, label)
        bg_color = ViewerEnum.BACKGROUND_COLOR.value
        text_color = tuple(map(lambda i, j: i - j, (255, 255, 255),
                               bg_color))
        text_sel_color = text_color
        style_dict = {
            'QSpinBox': {
                'background': 'rgba({0},{1},{2},20)'.format(*bg_color),
                'border': '1px solid rgb({0},{1},{2})'
                          .format(*ViewerEnum.ITEM_BORDER_COLOR.value),
                'border-radius': '3px',
                'color': 'rgba({0},{1},{2},230)'.format(*text_color),
                'selection-background-color': 'rgba({0},{1},{2},100)'
                                              .format(*text_sel_color),
            }
        }
        stylesheet = ''
        for css_class, css in style_dict.items():
            style = '{} {{\n'.format(css_class)
            for elm_name, elm_val in css.items():
                style += '  {}:{};\n'.format(elm_name, elm_val)
            style += '}\n'
            stylesheet += style
        spinner = QtWidgets.QSpinBox()
        spinner.setMinimum(min_val)
        spinner.setMaximum(max_val)
        spinner.setValue(value)
        spinner.setStyleSheet(stylesheet)
        spinner.valueChanged.connect(self.on_value_changed)
        spinner.clearFocus()
        self.set_custom_widget(spinner)
        self.widget().setMaximumWidth(140)

    @property
    def type_(self):
        return 'SpinnerNodeWidget'

    def get_value(self):
        """
        Returns the widget current value.

        Returns:
            int: current value.
        """
        return int(self.get_custom_widget().value())

    def set_value(self, value=0):
        """
        Sets the widget current value.

        Args:
            value (int): new value.
        """
        if value != self.get_value():
            self.get_custom_widget().setValue(value)
            self.on_value_changed()


class NodeDoubleSpinBox(NodeBaseWidget):
    """
    Displays as a ``QDoubleSpinBox`` in a node.

    .. inheritance-diagram:: NodeGraphQt.widgets.node_widgets.NodeDoubleSpinBox
        :parts: 1

    .. note::
        `To embed a` ``QDoubleSpinBox`` `in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_double_spinbox`
    """

    def __init__(self, parent=None, name='', label='', value=0.0, min_val=0.0,
                 max_val=100.0, decimals=2):
        super(NodeDoubleSpinBox, self).__init__(parent, name, label)
        bg_color = ViewerEnum.BACKGROUND_COLOR.value
        text_color = tuple(map(lambda i, j: i - j, (255, 255, 255),
                               bg_color))
        text_sel_color = text_color
        style_dict = {
            'QDoubleSpinBox': {
                'background': 'rgba({0},{1},{2},20)'.format(*bg_color),
                'border': '1px solid rgb({0},{1},{2})'
                          .format(*ViewerEnum.ITEM_BORDER_COLOR.value),
                'border-radius': '3px',
                'color': 'rgba({0},{1},{2},230)'.format(*text_color),
                'selection-background-color': 'rgba({0},{1},{2},100)'
                                              .format(*text_sel_color),
            }
        }
        stylesheet = ''
        for css_class, css in style_dict.items():
            style = '{} {{\n'.format(css_class)
            for elm_name, elm_val in css.items():
                style += '  {}:{};\n'.format(elm_name, elm_val)
            style += '}\n'
            stylesheet += style
        spinner = QtWidgets.QDoubleSpinBox()
        spinner.setMinimum(min_val)
        spinner.setMaximum(max_val)
        spinner.setDecimals(decimals)
        spinner.setValue(value)
        spinner.setStyleSheet(stylesheet)
        spinner.valueChanged.connect(self.on_value_changed)
        spinner.clearFocus()
        self.set_custom_widget(spinner)
        self.widget().setMaximumWidth(140)

    @property
    def type_(self):
        return 'DoubleSpinBoxNodeWidget'

    def get_value(self):
        """
        Returns the widget current value.

        Returns:
            float: current value.
        """
        return float(self.get_custom_widget().value())

    def set_value(self, value=0.0):
        """
        Sets the widget current value.

        Args:
            value (float): new value.
        """
        if value != self.get_value():
            self.get_custom_widget().setValue(value)
            self.on_value_changed()


class NodeColorPicker(NodeBaseWidget):
    """
    Displays as a Color Picker (RGB) in a node.

    .. inheritance-diagram:: NodeGraphQt.widgets.node_widgets.NodeColorPicker
        :parts: 1

    .. note::
        `To embed a Color Picker in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_color_picker`
    """

    def __init__(self, parent=None, name='', label='', color=(0, 0, 0)):
        super(NodeColorPicker, self).__init__(parent, name, label)
        self._color = color
        button = QtWidgets.QPushButton()
        button.setMaximumWidth(140)
        button.setMinimumHeight(24)
        button.clicked.connect(self._on_color_dialog)
        self.set_custom_widget(button)
        self._update_button_color()

    def _on_color_dialog(self):
        """Open color picker dialog."""
        current_color = QtGui.QColor(*self._color)
        color = QtWidgets.QColorDialog.getColor(current_color, None, 'Select Color')
        if color.isValid():
            self._color = (color.red(), color.green(), color.blue())
            self._update_button_color()
            self.on_value_changed()

    def _update_button_color(self):
        """Update button background to reflect current color."""
        button = self.get_custom_widget()
        r, g, b = self._color
        button.setStyleSheet(
            'QPushButton {{ background-color: rgb({},{},{}); '
            'border: 1px solid rgb(100,100,100); border-radius: 3px; }}'
            .format(r, g, b)
        )

    @property
    def type_(self):
        return 'ColorPickerNodeWidget'

    def get_value(self):
        """
        Returns the widget current color value as RGB tuple.

        Returns:
            tuple: (r, g, b) values 0-255.
        """
        return self._color

    def set_value(self, color=(0, 0, 0)):
        """
        Sets the widget current color value.

        Args:
            color (tuple): RGB tuple (r, g, b) values 0-255.
        """
        if color != self._color:
            self._color = color
            self._update_button_color()
            self.on_value_changed()


class NodeColor4Picker(NodeBaseWidget):
    """
    Displays as a Color Picker (RGBA) in a node.

    .. inheritance-diagram:: NodeGraphQt.widgets.node_widgets.NodeColor4Picker
        :parts: 1

    .. note::
        `To embed a Color Picker (RGBA) in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_color4_picker`
    """

    def __init__(self, parent=None, name='', label='', color=(0, 0, 0, 255)):
        super(NodeColor4Picker, self).__init__(parent, name, label)
        self._color = color
        button = QtWidgets.QPushButton()
        button.setMaximumWidth(140)
        button.setMinimumHeight(24)
        button.clicked.connect(self._on_color_dialog)
        self.set_custom_widget(button)
        self._update_button_color()

    def _on_color_dialog(self):
        """Open color picker dialog with alpha support."""
        current_color = QtGui.QColor(*self._color)
        color = QtWidgets.QColorDialog.getColor(
            current_color, None, 'Select Color',
            QtWidgets.QColorDialog.ShowAlphaChannel
        )
        if color.isValid():
            self._color = (color.red(), color.green(), color.blue(), color.alpha())
            self._update_button_color()
            self.on_value_changed()

    def _update_button_color(self):
        """Update button background to reflect current color."""
        button = self.get_custom_widget()
        r, g, b, a = self._color
        button.setStyleSheet(
            'QPushButton {{ background-color: rgba({},{},{},{}); '
            'border: 1px solid rgb(100,100,100); border-radius: 3px; }}'
            .format(r, g, b, a)
        )

    @property
    def type_(self):
        return 'Color4PickerNodeWidget'

    def get_value(self):
        """
        Returns the widget current color value as RGBA tuple.

        Returns:
            tuple: (r, g, b, a) values 0-255.
        """
        return self._color

    def set_value(self, color=(0, 0, 0, 255)):
        """
        Sets the widget current color value.

        Args:
            color (tuple): RGBA tuple (r, g, b, a) values 0-255.
        """
        if color != self._color:
            self._color = color
            self._update_button_color()
            self.on_value_changed()


class NodeSlider(NodeBaseWidget):
    """
    Displays as a Slider (Int) in a node.

    .. inheritance-diagram:: NodeGraphQt.widgets.node_widgets.NodeSlider
        :parts: 1

    .. note::
        `To embed an Integer Slider in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_slider`
    """

    def __init__(self, parent=None, name='', label='', value=0, min_val=0, max_val=100):
        super(NodeSlider, self).__init__(parent, name, label)
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(value)
        slider.setMinimumWidth(100)
        slider.setMaximumWidth(140)
        slider.valueChanged.connect(self.on_value_changed)
        self.set_custom_widget(slider)

    @property
    def type_(self):
        return 'SliderNodeWidget'

    def get_value(self):
        """
        Returns the widget current value.

        Returns:
            int: current slider value.
        """
        return int(self.get_custom_widget().value())

    def set_value(self, value=0):
        """
        Sets the widget current value.

        Args:
            value (int): new slider value.
        """
        if value != self.get_value():
            self.get_custom_widget().setValue(value)
            self.on_value_changed()


class NodeDoubleSlider(NodeBaseWidget):
    """
    Displays as a Slider (Double) in a node.

    .. inheritance-diagram:: NodeGraphQt.widgets.node_widgets.NodeDoubleSlider
        :parts: 1

    .. note::
        `To embed a Double Slider in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_double_slider`
    """

    def __init__(self, parent=None, name='', label='', value=0.0, min_val=0.0, 
                 max_val=100.0, decimals=2):
        super(NodeDoubleSlider, self).__init__(parent, name, label)
        self._decimals = decimals
        self._min_val = min_val
        self._max_val = max_val
        
        # QSlider only works with integers, so we scale the values
        self._scale = 10 ** decimals
        
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setMinimum(int(min_val * self._scale))
        slider.setMaximum(int(max_val * self._scale))
        slider.setValue(int(value * self._scale))
        slider.setMinimumWidth(100)
        slider.setMaximumWidth(140)
        slider.valueChanged.connect(self.on_value_changed)
        self.set_custom_widget(slider)

    @property
    def type_(self):
        return 'DoubleSliderNodeWidget'

    def get_value(self):
        """
        Returns the widget current value.

        Returns:
            float: current slider value.
        """
        return round(self.get_custom_widget().value() / self._scale, self._decimals)

    def set_value(self, value=0.0):
        """
        Sets the widget current value.

        Args:
            value (float): new slider value.
        """
        if value != self.get_value():
            self.get_custom_widget().setValue(int(value * self._scale))
            self.on_value_changed()


class NodeFileOpen(NodeBaseWidget):
    """
    Displays as a file selector widget in a node.

    .. inheritance-diagram:: NodeGraphQt.widgets.node_widgets.NodeFileOpen
        :parts: 1

    .. note::
        `To embed a file selector in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_file_open`
    """

    def __init__(self, parent=None, name='', label='', file_path='', file_filter='All Files (*)'):
        super(NodeFileOpen, self).__init__(parent, name, label)
        self._file_path = file_path
        self._file_filter = file_filter
        
        button = QtWidgets.QPushButton('Browse...')
        button.setMaximumWidth(140)
        button.setMinimumHeight(24)
        button.clicked.connect(self._on_file_dialog)
        self.set_custom_widget(button)

    def _on_file_dialog(self):
        """Open file dialog."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, 'Select File', self._file_path, self._file_filter
        )
        if file_path:
            self._file_path = file_path
            self.on_value_changed()

    @property
    def type_(self):
        return 'FileOpenNodeWidget'

    def get_value(self):
        """
        Returns the selected file path.

        Returns:
            str: file path.
        """
        return self._file_path

    def set_value(self, file_path=''):
        """
        Sets the file path.

        Args:
            file_path (str): new file path.
        """
        if file_path != self._file_path:
            self._file_path = file_path
            self.on_value_changed()


class NodeFileSave(NodeBaseWidget):
    """
    Displays as a file save widget in a node.

    .. inheritance-diagram:: NodeGraphQt.widgets.node_widgets.NodeFileSave
        :parts: 1

    .. note::
        `To embed a file save selector in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_file_save`
    """

    def __init__(self, parent=None, name='', label='', file_path='', file_filter='All Files (*)'):
        super(NodeFileSave, self).__init__(parent, name, label)
        self._file_path = file_path
        self._file_filter = file_filter
        
        button = QtWidgets.QPushButton('Save As...')
        button.setMaximumWidth(140)
        button.setMinimumHeight(24)
        button.clicked.connect(self._on_file_dialog)
        self.set_custom_widget(button)

    def _on_file_dialog(self):
        """Open file save dialog."""
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            None, 'Save File', self._file_path, self._file_filter
        )
        if file_path:
            self._file_path = file_path
            self.on_value_changed()

    @property
    def type_(self):
        return 'FileSaveNodeWidget'

    def get_value(self):
        """
        Returns the selected file path.

        Returns:
            str: file path.
        """
        return self._file_path

    def set_value(self, file_path=''):
        """
        Sets the file path.

        Args:
            file_path (str): new file path.
        """
        if file_path != self._file_path:
            self._file_path = file_path
            self.on_value_changed()


class NodeVector2(NodeBaseWidget):
    """
    Displays as a Vector2 widget in a node.

    .. inheritance-diagram:: NodeGraphQt.widgets.node_widgets.NodeVector2
        :parts: 1

    .. note::
        `To embed a Vector2 widget in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_vector2`
    """

    def __init__(self, parent=None, name='', label='', value=(0.0, 0.0)):
        super(NodeVector2, self).__init__(parent, name, label)
        
        bg_color = ViewerEnum.BACKGROUND_COLOR.value
        text_color = tuple(map(lambda i, j: i - j, (255, 255, 255), bg_color))
        text_sel_color = text_color
        style_dict = {
            'QDoubleSpinBox': {
                'background': 'rgba({0},{1},{2},20)'.format(*bg_color),
                'border': '1px solid rgb({0},{1},{2})'
                          .format(*ViewerEnum.ITEM_BORDER_COLOR.value),
                'border-radius': '3px',
                'color': 'rgba({0},{1},{2},230)'.format(*text_color),
                'selection-background-color': 'rgba({0},{1},{2},100)'
                                              .format(*text_sel_color),
            }
        }
        stylesheet = ''
        for css_class, css in style_dict.items():
            style = '{} {{\n'.format(css_class)
            for elm_name, elm_val in css.items():
                style += '  {}:{};\n'.format(elm_name, elm_val)
            style += '}\n'
            stylesheet += style
        
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        self._spin_x = QtWidgets.QDoubleSpinBox()
        self._spin_x.setMinimum(-999999.0)
        self._spin_x.setMaximum(999999.0)
        self._spin_x.setValue(value[0])
        self._spin_x.setStyleSheet(stylesheet)
        self._spin_x.setPrefix('X: ')
        self._spin_x.valueChanged.connect(self.on_value_changed)
        
        self._spin_y = QtWidgets.QDoubleSpinBox()
        self._spin_y.setMinimum(-999999.0)
        self._spin_y.setMaximum(999999.0)
        self._spin_y.setValue(value[1])
        self._spin_y.setStyleSheet(stylesheet)
        self._spin_y.setPrefix('Y: ')
        self._spin_y.valueChanged.connect(self.on_value_changed)
        
        layout.addWidget(self._spin_x)
        layout.addWidget(self._spin_y)
        
        self.set_custom_widget(widget)
        self.widget().setMaximumWidth(280)

    @property
    def type_(self):
        return 'Vector2NodeWidget'

    def get_value(self):
        """
        Returns the widget current value.

        Returns:
            tuple: (x, y) vector values.
        """
        return (self._spin_x.value(), self._spin_y.value())

    def set_value(self, value=(0.0, 0.0)):
        """
        Sets the widget current value.

        Args:
            value (tuple): (x, y) vector values.
        """
        if value != self.get_value():
            self._spin_x.setValue(value[0])
            self._spin_y.setValue(value[1])
            self.on_value_changed()


class NodeVector3(NodeBaseWidget):
    """
    Displays as a Vector3 widget in a node.

    .. inheritance-diagram:: NodeGraphQt.widgets.node_widgets.NodeVector3
        :parts: 1

    .. note::
        `To embed a Vector3 widget in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_vector3`
    """

    def __init__(self, parent=None, name='', label='', value=(0.0, 0.0, 0.0)):
        super(NodeVector3, self).__init__(parent, name, label)
        
        bg_color = ViewerEnum.BACKGROUND_COLOR.value
        text_color = tuple(map(lambda i, j: i - j, (255, 255, 255), bg_color))
        text_sel_color = text_color
        style_dict = {
            'QDoubleSpinBox': {
                'background': 'rgba({0},{1},{2},20)'.format(*bg_color),
                'border': '1px solid rgb({0},{1},{2})'
                          .format(*ViewerEnum.ITEM_BORDER_COLOR.value),
                'border-radius': '3px',
                'color': 'rgba({0},{1},{2},230)'.format(*text_color),
                'selection-background-color': 'rgba({0},{1},{2},100)'
                                              .format(*text_sel_color),
            }
        }
        stylesheet = ''
        for css_class, css in style_dict.items():
            style = '{} {{\n'.format(css_class)
            for elm_name, elm_val in css.items():
                style += '  {}:{};\n'.format(elm_name, elm_val)
            style += '}\n'
            stylesheet += style
        
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        self._spin_x = QtWidgets.QDoubleSpinBox()
        self._spin_x.setMinimum(-999999.0)
        self._spin_x.setMaximum(999999.0)
        self._spin_x.setValue(value[0])
        self._spin_x.setStyleSheet(stylesheet)
        self._spin_x.setPrefix('X: ')
        self._spin_x.valueChanged.connect(self.on_value_changed)
        
        self._spin_y = QtWidgets.QDoubleSpinBox()
        self._spin_y.setMinimum(-999999.0)
        self._spin_y.setMaximum(999999.0)
        self._spin_y.setValue(value[1])
        self._spin_y.setStyleSheet(stylesheet)
        self._spin_y.setPrefix('Y: ')
        self._spin_y.valueChanged.connect(self.on_value_changed)
        
        self._spin_z = QtWidgets.QDoubleSpinBox()
        self._spin_z.setMinimum(-999999.0)
        self._spin_z.setMaximum(999999.0)
        self._spin_z.setValue(value[2])
        self._spin_z.setStyleSheet(stylesheet)
        self._spin_z.setPrefix('Z: ')
        self._spin_z.valueChanged.connect(self.on_value_changed)
        
        layout.addWidget(self._spin_x)
        layout.addWidget(self._spin_y)
        layout.addWidget(self._spin_z)
        
        self.set_custom_widget(widget)
        self.widget().setMaximumWidth(420)

    @property
    def type_(self):
        return 'Vector3NodeWidget'

    def get_value(self):
        """
        Returns the widget current value.

        Returns:
            tuple: (x, y, z) vector values.
        """
        return (self._spin_x.value(), self._spin_y.value(), self._spin_z.value())

    def set_value(self, value=(0.0, 0.0, 0.0)):
        """
        Sets the widget current value.

        Args:
            value (tuple): (x, y, z) vector values.
        """
        if value != self.get_value():
            self._spin_x.setValue(value[0])
            self._spin_y.setValue(value[1])
            self._spin_z.setValue(value[2])
            self.on_value_changed()


class NodeVector4(NodeBaseWidget):
    """
    Displays as a Vector4 widget in a node.

    .. inheritance-diagram:: NodeGraphQt.widgets.node_widgets.NodeVector4
        :parts: 1

    .. note::
        `To embed a Vector4 widget in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_vector4`
    """

    def __init__(self, parent=None, name='', label='', value=(0.0, 0.0, 0.0, 0.0)):
        super(NodeVector4, self).__init__(parent, name, label)
        
        bg_color = ViewerEnum.BACKGROUND_COLOR.value
        text_color = tuple(map(lambda i, j: i - j, (255, 255, 255), bg_color))
        text_sel_color = text_color
        style_dict = {
            'QDoubleSpinBox': {
                'background': 'rgba({0},{1},{2},20)'.format(*bg_color),
                'border': '1px solid rgb({0},{1},{2})'
                          .format(*ViewerEnum.ITEM_BORDER_COLOR.value),
                'border-radius': '3px',
                'color': 'rgba({0},{1},{2},230)'.format(*text_color),
                'selection-background-color': 'rgba({0},{1},{2},100)'
                                              .format(*text_sel_color),
            }
        }
        stylesheet = ''
        for css_class, css in style_dict.items():
            style = '{} {{\n'.format(css_class)
            for elm_name, elm_val in css.items():
                style += '  {}:{};\n'.format(elm_name, elm_val)
            style += '}\n'
            stylesheet += style
        
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        self._spin_x = QtWidgets.QDoubleSpinBox()
        self._spin_x.setMinimum(-999999.0)
        self._spin_x.setMaximum(999999.0)
        self._spin_x.setValue(value[0])
        self._spin_x.setStyleSheet(stylesheet)
        self._spin_x.setPrefix('X: ')
        self._spin_x.valueChanged.connect(self.on_value_changed)
        
        self._spin_y = QtWidgets.QDoubleSpinBox()
        self._spin_y.setMinimum(-999999.0)
        self._spin_y.setMaximum(999999.0)
        self._spin_y.setValue(value[1])
        self._spin_y.setStyleSheet(stylesheet)
        self._spin_y.setPrefix('Y: ')
        self._spin_y.valueChanged.connect(self.on_value_changed)
        
        self._spin_z = QtWidgets.QDoubleSpinBox()
        self._spin_z.setMinimum(-999999.0)
        self._spin_z.setMaximum(999999.0)
        self._spin_z.setValue(value[2])
        self._spin_z.setStyleSheet(stylesheet)
        self._spin_z.setPrefix('Z: ')
        self._spin_z.valueChanged.connect(self.on_value_changed)
        
        self._spin_w = QtWidgets.QDoubleSpinBox()
        self._spin_w.setMinimum(-999999.0)
        self._spin_w.setMaximum(999999.0)
        self._spin_w.setValue(value[3])
        self._spin_w.setStyleSheet(stylesheet)
        self._spin_w.setPrefix('W: ')
        self._spin_w.valueChanged.connect(self.on_value_changed)
        
        layout.addWidget(self._spin_x)
        layout.addWidget(self._spin_y)
        layout.addWidget(self._spin_z)
        layout.addWidget(self._spin_w)
        
        self.set_custom_widget(widget)
        self.widget().setMaximumWidth(560)

    @property
    def type_(self):
        return 'Vector4NodeWidget'

    def get_value(self):
        """
        Returns the widget current value.

        Returns:
            tuple: (x, y, z, w) vector values.
        """
        return (self._spin_x.value(), self._spin_y.value(), 
                self._spin_z.value(), self._spin_w.value())

    def set_value(self, value=(0.0, 0.0, 0.0, 0.0)):
        """
        Sets the widget current value.

        Args:
            value (tuple): (x, y, z, w) vector values.
        """
        if value != self.get_value():
            self._spin_x.setValue(value[0])
            self._spin_y.setValue(value[1])
            self._spin_z.setValue(value[2])
            self._spin_w.setValue(value[3])
            self.on_value_changed()


class NodeFloat(NodeBaseWidget):
    """
    Displays as a Float line edit widget in a node.

    .. inheritance-diagram:: NodeGraphQt.widgets.node_widgets.NodeFloat
        :parts: 1

    .. note::
        `To embed a Float line edit in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_float`
    """

    def __init__(self, parent=None, name='', label='', value=0.0):
        super(NodeFloat, self).__init__(parent, name, label)
        bg_color = ViewerEnum.BACKGROUND_COLOR.value
        text_color = tuple(map(lambda i, j: i - j, (255, 255, 255),
                               bg_color))
        text_sel_color = text_color
        style_dict = {
            'QLineEdit': {
                'background': 'rgba({0},{1},{2},20)'.format(*bg_color),
                'border': '1px solid rgb({0},{1},{2})'
                          .format(*ViewerEnum.ITEM_BORDER_COLOR.value),
                'border-radius': '3px',
                'color': 'rgba({0},{1},{2},230)'.format(*text_color),
                'selection-background-color': 'rgba({0},{1},{2},100)'
                                              .format(*text_sel_color),
            }
        }
        stylesheet = ''
        for css_class, css in style_dict.items():
            style = '{} {{\n'.format(css_class)
            for elm_name, elm_val in css.items():
                style += '  {}:{};\n'.format(elm_name, elm_val)
            style += '}\n'
            stylesheet += style
        
        ledit = QtWidgets.QLineEdit()
        ledit.setValidator(QtGui.QDoubleValidator())
        ledit.setText(str(value))
        ledit.setStyleSheet(stylesheet)
        ledit.setAlignment(QtCore.Qt.AlignCenter)
        ledit.editingFinished.connect(self.on_value_changed)
        ledit.clearFocus()
        self.set_custom_widget(ledit)
        self.widget().setMaximumWidth(140)

    @property
    def type_(self):
        return 'FloatNodeWidget'

    def get_value(self):
        """
        Returns the widget current value.

        Returns:
            float: current value.
        """
        try:
            return float(self.get_custom_widget().text())
        except ValueError:
            return 0.0

    def set_value(self, value=0.0):
        """
        Sets the widget current value.

        Args:
            value (float): new value.
        """
        if value != self.get_value():
            self.get_custom_widget().setText(str(value))
            self.on_value_changed()


class NodeInt(NodeBaseWidget):
    """
    Displays as an Int line edit widget in a node.

    .. inheritance-diagram:: NodeGraphQt.widgets.node_widgets.NodeInt
        :parts: 1

    .. note::
        `To embed an Int line edit in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_int`
    """

    def __init__(self, parent=None, name='', label='', value=0):
        super(NodeInt, self).__init__(parent, name, label)
        bg_color = ViewerEnum.BACKGROUND_COLOR.value
        text_color = tuple(map(lambda i, j: i - j, (255, 255, 255),
                               bg_color))
        text_sel_color = text_color
        style_dict = {
            'QLineEdit': {
                'background': 'rgba({0},{1},{2},20)'.format(*bg_color),
                'border': '1px solid rgb({0},{1},{2})'
                          .format(*ViewerEnum.ITEM_BORDER_COLOR.value),
                'border-radius': '3px',
                'color': 'rgba({0},{1},{2},230)'.format(*text_color),
                'selection-background-color': 'rgba({0},{1},{2},100)'
                                              .format(*text_sel_color),
            }
        }
        stylesheet = ''
        for css_class, css in style_dict.items():
            style = '{} {{\n'.format(css_class)
            for elm_name, elm_val in css.items():
                style += '  {}:{};\n'.format(elm_name, elm_val)
            style += '}\n'
            stylesheet += style
        
        ledit = QtWidgets.QLineEdit()
        ledit.setValidator(QtGui.QIntValidator())
        ledit.setText(str(value))
        ledit.setStyleSheet(stylesheet)
        ledit.setAlignment(QtCore.Qt.AlignCenter)
        ledit.editingFinished.connect(self.on_value_changed)
        ledit.clearFocus()
        self.set_custom_widget(ledit)
        self.widget().setMaximumWidth(140)

    @property
    def type_(self):
        return 'IntNodeWidget'

    def get_value(self):
        """
        Returns the widget current value.

        Returns:
            int: current value.
        """
        try:
            return int(self.get_custom_widget().text())
        except ValueError:
            return 0

    def set_value(self, value=0):
        """
        Sets the widget current value.

        Args:
            value (int): new value.
        """
        if value != self.get_value():
            self.get_custom_widget().setText(str(value))
            self.on_value_changed()